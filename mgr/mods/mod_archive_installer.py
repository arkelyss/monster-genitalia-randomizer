from dataclasses import dataclass
from functools import partial
import logging
from typing import Callable, ClassVar, override
import zipfile
from PySide6.QtCore import QObject, Signal
import py7zr
from py7zr import callbacks
from py7zr.io import Py7zBytesIO, WriterFactory
from rarfile import RarFile

from pathlib import Path

from mgr.core.re_patterns import RELATIVE_MOD_PATH_PATTERN, RelativeModPathKeys
from mgr.mods.models.enums import SupportedArchiveTypes, SupportedModfileTypes

logger = logging.getLogger(__name__)

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

MAX_FILE_BYTES  = 500 * MB
MAX_TOTAL_BYTES = 2   * GB 

@dataclass
class ModArchive:
    name: str
    file: Path
    contents: list[str]

@dataclass(frozen=True, slots=True)
class InstallProgress:
    """Snapshot of extraction progress."""

    archive_name: str
    archive_index: int
    total_archives: int
    current_file: str
    archive_bytes_done: int
    archive_bytes_total: int
 
    @property
    def archive_fraction(self) -> float:
        if self.archive_bytes_total <= 0:
            return 0.0
        return min(self.archive_bytes_done / self.archive_bytes_total, 1.0)
 
    @property
    def batch_fraction(self) -> float:
        """Batch progress weighting each archive equally, with the current
        archive's byte progress interpolated in."""
        if self.total_archives <= 0:
            return 0.0
        return (self.archive_index + self.archive_fraction) / self.total_archives

class _ProgressState:
    """Internal extraction state. Produces InstallProgress snapshots."""
 
    def __init__(self, total_archives: int) -> None:
        self.total_archives: int = total_archives
        self.archive_index: int = 0
        self.archive_name: str = ""
        self.current_file: str = ""
        self.bytes_done: int = 0
        self.bytes_total: int = 0
 
    def begin_archive(self, index: int, name: str, bytes_total: int) -> None:
        self.archive_index = index
        self.archive_name = name
        self.current_file = ""
        self.bytes_done = 0
        self.bytes_total = bytes_total
 
    def snapshot(self) -> InstallProgress:
        return InstallProgress(
            archive_name=self.archive_name,
            archive_index=self.archive_index,
            total_archives=self.total_archives,
            current_file=self.current_file,
            archive_bytes_done=self.bytes_done,
            archive_bytes_total=self.bytes_total,
        )

class StreamIO(py7zr.Py7zIO):
    """In-memory write target for py7zr with a hard size limit."""
 
    def __init__(self, filename: str, limit: int) -> None:
        super().__init__()
        self.filename: str = filename
        self.limit: int = limit
        self._buffer: Py7zBytesIO = Py7zBytesIO(filename=filename, limit=limit)
 
    @override
    def write(self, s: bytes | bytearray) -> int:
        if self.size() + len(s) > self.limit:
            raise RuntimeError(
                f'"{self.filename}" exceeds the per-file extraction limit ' +
                f'({self.limit} bytes).'
            )
        return self._buffer.write(s)
 
    @override
    def read(self, size: int | None = None) -> bytes:
        return self._buffer.read(size)
 
    @override
    def seek(self, offset: int, whence: int = 0) -> int:
        return self._buffer.seek(offset, whence)
 
    @override
    def flush(self) -> None:
        return self._buffer.flush()
 
    @override
    def size(self) -> int:
        return self._buffer.size()
 
    def getvalue(self) -> bytes:
        """Retrieve all extracted bytes."""
        self.seek(0)
        return self.read()


class InMemoryFactory(WriterFactory):
    """Factory py7zr calls once per archived file during extraction."""
 
    def __init__(self, adjust_path_fn: Callable[[str], str], limit: int) -> None:
        self._adjust_path_fn: Callable[[str], str] = adjust_path_fn
        self.limit: int = limit
        self.products: dict[str, StreamIO] = {}
 
    @override
    def create(self, filename: str) -> StreamIO:
        new_filename = self._adjust_path_fn(filename)
        stream = StreamIO(new_filename, limit=self.limit)
        self.products[new_filename] = stream
        return stream

# py7zr has its own internal reporting thread. I am not aware of a way to control which thread it goes to.
# We can subclass to access the reporting methods, but since they exist on another thread we should avoid
# trying to touch Qt objects directly.
# Instead, we will mutate our own internal state and emit that back for Qt listeners.

# Important notes:
# - report_update(bytes) delivers byte deltas (one per file)
# - Extracted directories also trigger report_start and report_end events
# - Parameter 'report_bytes' of the report_start method delivers innaccurate information, so size queries should be
#   retrieved from SevenZipFile.list() instead

class _SevenZipProgressCallback(callbacks.ExtractCallback):
    """Bridges py7zr's callback events for progress reporting."""
 
    def __init__(
        self,
        target_names: list[str],
        progress_state: _ProgressState,
        emit_snapshot: Callable[[InstallProgress], None],
    ) -> None:
        self._target_names: list[str] = target_names
        self._state: _ProgressState = progress_state
        self._emit_snapshot: Callable[[InstallProgress], None] = emit_snapshot
 
    @override
    def report_start_preparation(self) -> None:
        pass
 
    @override
    def report_start(self, processing_file_path: str, processing_bytes: str) -> None:
        if processing_file_path in self._target_names:
            self._state.current_file = processing_file_path
            self._emit_snapshot(self._state.snapshot())
 
    @override
    def report_update(self, decompressed_bytes: str) -> None:
        # Deltas may include bytes from non-target files (such as directories),
        # so we only count it if the current file is in our targets.
        if self._state.current_file in self._target_names:
            self._state.bytes_done += int(decompressed_bytes)
            self._emit_snapshot(self._state.snapshot())
 
    @override
    def report_end(self, processing_file_path: str, wrote_bytes: str) -> None:
        pass
 
    @override
    def report_warning(self, message: str) -> None:
        logger.warning(f"py7zr warning: {message}")
 
    @override
    def report_postprocess(self) -> None:
        pass


class ArchiveExtractor(QObject):
    """Extracts mod archives to the MGR mods directory.
 
    Designed to run on a worker QThread. All signals are safe to connect to
    slots on the main thread.
    """
 
    extraction_started: Signal = Signal()
    extraction_progress: Signal = Signal(object)  # InstallProgress
    archive_failed: Signal = Signal(str, str)  # (archive name, reason)
    extraction_finished: Signal = Signal()

    # Knowledge Note:
    # ClassVar allows a variable to be shared in memory between all instances of a class that reference it,
    # regardless of how many instances there are. This makes it highly efficient, as placing it inside __init__
    # would result in a new instance of that variable being created in memory for each instance of the class.
    _EXTRACTOR_METHOD_NAMES: ClassVar[dict[str, str]] = {
        SupportedArchiveTypes.ZIP.value: "_extract_zip",
        SupportedArchiveTypes.SEVENZIP.value: "_extract_sevenzip",
        SupportedArchiveTypes.RAR.value: "_extract_rar",
    }
 
    def __init__(
        self,
        archive_files: list[Path],
        mgr_mods_dir: Path,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._archive_files: list[Path] = archive_files
        self._mgr_mods_dir: Path = mgr_mods_dir
 
    def install_archives(self) -> None:
        """Extracts archives and skips/reports any that fail."""

        self.extraction_started.emit()
        progress_state = _ProgressState(total_archives=len(self._archive_files))
        try:
            for archive_index, archive_path in enumerate(self._archive_files):
                try:
                    self._install_single_archive(archive_path, archive_index, progress_state)
                except Exception as exc:
                    logger.exception(f"Failed to extract {archive_path}, skipping")
                    self.archive_failed.emit(archive_path.name, str(exc))
        finally:
            self.extraction_finished.emit()
    
    # Install a single archive from the list. Return an error for unsupported archive types.
    def _install_single_archive(self, archive_path: Path, archive_index: int, progress_state: _ProgressState) -> None:
        extractor = self._get_extractor(archive_path)
        if extractor is None:
            raise ValueError(f"Unsupported archive type: {archive_path.suffix}")
        extractor(archive_path, self._mgr_mods_dir, archive_index, progress_state)
 
    # Attempts to return an extractor for an archive's filetype
    def _get_extractor(
        self, archive_path: Path
    ) -> Callable[[Path, Path, int, _ProgressState], None] | None:
        method_name = self._EXTRACTOR_METHOD_NAMES.get(archive_path.suffix.lower())
        return getattr(self, method_name) if method_name else None
 
    
    # Zip extractor
    # Dev Note: Can throw exceptions through _check_size_limits(). May need GUI notification instead of app crash.
    def _extract_zip(
        self, archive_file: Path, output_dir: Path, index: int, state: _ProgressState
    ) -> None:
        with zipfile.ZipFile(archive_file, "r") as archive_ref:
            items = [item for item in archive_ref.namelist() if not archive_ref.getinfo(item).is_dir()]
            targets = self._filter_targets(items)
            sizes = {target: archive_ref.getinfo(target).file_size for target in targets}
            self._check_size_limits(archive_file, sizes)
 
            state.begin_archive(index, archive_file.name, sum(sizes.values()))
            self.extraction_progress.emit(state.snapshot())
 
            mod_name = archive_file.stem
            for target in targets:
                state.current_file = target
                raw_bytes = archive_ref.read(target)
                adjusted_path = self._adjust_target_path_for_mgr(target, mod_name)
                self._write_file(raw_bytes, adjusted_path, output_dir)
                state.bytes_done += sizes[target]
                self.extraction_progress.emit(state.snapshot())
 
    # Rar extractor
    # The rarfile package ships no stubs, but mirrors the zipfile structure closely.
    # I've had pyright generate a local stub in typings/rarfile to keep checkers happy.
    # Dev Note: Can throw exceptions through _check_size_limits(). May need GUI notification instead of app crash.
    def _extract_rar(self, archive_file: Path, output_dir: Path, index: int, state: _ProgressState) -> None:
        with RarFile(archive_file, "r") as archive_ref:
            items = [item for item in archive_ref.namelist() if not archive_ref.getinfo(item).is_dir()]
            targets = self._filter_targets(items)
            sizes = {target: archive_ref.getinfo(target).file_size for target in targets}
            self._check_size_limits(archive_file, sizes)
 
            state.begin_archive(index, archive_file.name, sum(sizes.values()))
            self.extraction_progress.emit(state.snapshot())
 
            mod_name = archive_file.stem
            for target in targets:
                state.current_file = target
                raw_bytes = archive_ref.read(target)
                adjusted_path = self._adjust_target_path_for_mgr(target, mod_name)
                self._write_file(raw_bytes, adjusted_path, output_dir)
                state.bytes_done += sizes[target]
                self.extraction_progress.emit(state.snapshot())
 
    # 7z extractor
    # Dev Note: Can throw exceptions through _check_size_limits(). May need GUI notification instead of app crash.
    def _extract_sevenzip(self, archive_file: Path, output_dir: Path, index: int, state: _ProgressState) -> None:
        mod_name = archive_file.stem
        with py7zr.SevenZipFile(archive_file, mode="r") as archive_ref:
            file_info = archive_ref.list()
            items = [info.filename for info in file_info if not info.is_directory]
            targets = self._filter_targets(items)
            sizes = {info.filename: info.uncompressed for info in file_info if info.filename in targets}
            self._check_size_limits(archive_file, sizes)
 
            state.begin_archive(index, archive_file.name, sum(sizes.values()))
 
            factory = InMemoryFactory(
                adjust_path_fn = partial(self._adjust_target_path_for_mgr, new_parent_dir_name = mod_name),
                limit = MAX_FILE_BYTES,
            )

            # SevenZipFile does not give us an easy way to track per-file progress.
            # To work around this, extract targets to memory first and emit that progress.
            # Progress is reported during decompression via the callback, which py7zr invokes from its own reporter
            # thread. Emitting a Qt signal from there is safe.
            callback = _SevenZipProgressCallback(
                target_names = targets,
                progress_state = state,
                emit_snapshot = self.extraction_progress.emit,
            )
            archive_ref.extract(targets=targets, factory=factory, callback=callback)
 
        # Move in-memory bytes to disk. Fast relative to decompression, so we don't do per-file emits here.
        for adjusted_path, stream in factory.products.items():
            self._write_file(stream.getvalue(), adjusted_path, output_dir)
 
        # Adjust bytes_done to bytes_total if they are not equal (they should be, at this point).
        # This catches edge cases for missing bytes.
        if state.bytes_done != state.bytes_total:
            state.bytes_done = state.bytes_total
            self.extraction_progress.emit(state.snapshot())
 
    # Return archive items whose parent path contains regex matches to our relative path pattern (e.g. ##/em##/dir_name)
    @staticmethod
    def _filter_targets(archive_items: list[str]) -> list[str]:
        return [
            item
            for item in archive_items
            if Path(item).suffix.lower() in SupportedModfileTypes
            and RELATIVE_MOD_PATH_PATTERN.search(str(Path(item).parent))
        ]
 
    # Reject archives whose declared sizes exceed extraction limits. Uses header metadata only (nothing is decompressed).
    # Sizes can lie (especially zip bombs) so with 7z we additionally
    # enforce MAX_FILE_BYTES at write time via StreamIO.
    @staticmethod
    def _check_size_limits(archive_file: Path, modfile_sizes: dict[str, int]) -> None:
        oversized_modfiles = [modfile for modfile, size in modfile_sizes.items() if size > MAX_FILE_BYTES]
        if oversized_modfiles:
            raise ValueError(
                f"'{archive_file.name}' contains files over the " +
                f"{MAX_FILE_BYTES // MB} MB per-file limit: {oversized_modfiles[:3]}"
            )
        total = sum(modfile_sizes.values())
        if total > MAX_TOTAL_BYTES:
            raise ValueError(
                f"'{archive_file.name}' would extract {total // MB} MB, over the " +
                f"{MAX_TOTAL_BYTES // GB} GB limit."
            )
 
    @staticmethod
    def _write_file(raw_bytes: bytes, adjusted_path: str, output_dir: Path) -> None:
        output_path = output_dir / adjusted_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(raw_bytes)
 
    def _adjust_target_path_for_mgr(
        self, modfile_path: str, new_parent_dir_name: str
    ) -> str:
        """Constructs a new path for the target file, making it more identifiable to
        MGR by renaming the modfile's parent directory to mirror the original
        mod archive name."""
        pattern_match = RELATIVE_MOD_PATH_PATTERN.search(str(Path(modfile_path).parent))
        if pattern_match is None:
            raise ValueError(
                f"Extraction failed; path does not match mod layout: {modfile_path}"
            )
        match_groupdict = pattern_match.groupdict()
        new_path = (
            Path(match_groupdict[RelativeModPathKeys.MONSTER_ID_WITH_EM])
            / match_groupdict[RelativeModPathKeys.VARIANT_ID]
            / new_parent_dir_name
            / Path(modfile_path).name
        )
        return str(new_path)