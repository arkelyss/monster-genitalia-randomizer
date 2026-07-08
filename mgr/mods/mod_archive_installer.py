from dataclasses import dataclass, field
from functools import partial
import logging
import sys
from typing import Callable, override
import zipfile
from PySide6.QtCore import QObject, Signal
import py7zr
from py7zr.io import Py7zBytesIO, WriterFactory
from rarfile import RarFile
from mgr.core.exceptions import InvalidItemStructure

from pathlib import Path

from mgr.core.re_patterns import RELATIVE_MOD_PATH_PATTERN, RelativeModPathKeys
from mgr.mods.models.enums import SupportedArchiveTypes

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

@dataclass
class ExtractionTracker:
    all_mod_archives: list[str]

    current_archive_index: int = 0
    current_archive_targets: list[str] = field(default_factory=list)
    current_target_index: int = 0

    @property
    def current_archive_name(self):
        return Path(self.all_mod_archives[self.current_archive_index]).name

    @property
    def current_modfile_name(self):
        return self.current_archive_targets[self.current_target_index]

    @property
    def global_archive_progress_outof(self):
        position = self.current_archive_index + 1
        return f"{position}/{len(self.all_mod_archives)}"
    
    @property
    def global_archive_progress_percent(self):
        position = self.current_archive_index + 1
        return f"{(position / len(self.all_mod_archives)) * 100:.1f}%"

    @property
    def current_archive_progress_outof(self):
        position = self.current_target_index + 1
        return f"{position}/{len(self.current_archive_targets)}"

    @property
    def current_archive_progress_percent(self):
        position = self.current_target_index + 1
        return f"{(position / len(self.current_archive_targets)) * 100:.1f}%"


class StreamIO(py7zr.Py7zIO):
    def __init__(self, filename: str, limit: int) -> None:
        super().__init__()
        self.filename: str = filename
        self.limit: int = limit
        self._buffer: Py7zBytesIO = Py7zBytesIO(filename=self.filename, limit=self.limit)

    @override
    def write(self, s: bytes | bytearray) -> int:
        if self.size() < self.limit:
            return self._buffer.write(s)
        else:
            raise ValueError("Not enough memory to extract archive.")

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
        """Convenience method to retrieve all extracted bytes."""
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
        stream = StreamIO(new_filename, limit = self.limit)
        self.products[new_filename] = stream
        return stream

    
class ArchiveExtractor(QObject):
    on_progress: Signal = Signal(object)
    on_finished: Signal = Signal()

    def _extract_zip(self, archive_file: Path, output_dir: Path, extraction_tracker: ExtractionTracker):
        with zipfile.ZipFile(archive_file, 'r') as archive_ref:
            archive_items = archive_ref.namelist()
            modfile_targets = [item for item in archive_items if RELATIVE_MOD_PATH_PATTERN.search(str(Path(item).parent))]
            extraction_tracker.current_archive_targets = modfile_targets

            for index, target in enumerate(modfile_targets):
                raw_bytes: bytes = archive_ref.read(target)

                mod_name = archive_file.stem
                extraction_tracker.current_target_index = index
                adjusted_path = self._adjust_modfile_path_for_mgr(target, mod_name)
                
                output_path: Path = output_dir / adjusted_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(raw_bytes)

                self.on_progress.emit(extraction_tracker)
    
    def _extract_sevenzip(self, archive_file: Path, output_dir: Path, extraction_tracker: ExtractionTracker) -> None:
        with py7zr.SevenZipFile(archive_file, mode='r') as archive_ref:
            mod_name = archive_file.stem
            archive_items = archive_ref.namelist()
            modfile_targets = [item for item in archive_items if RELATIVE_MOD_PATH_PATTERN.search(str(Path(item).parent))]
            extraction_tracker.current_archive_targets = modfile_targets

            factory = InMemoryFactory(adjust_path_fn=partial(self._adjust_modfile_path_for_mgr, new_parent_dir_name = mod_name), limit=sys.maxsize)
            archive_ref.extract(targets=modfile_targets, factory=factory)

        for index, (target, stream) in enumerate(factory.products.items()):
            extraction_tracker.current_target_index = index
            data = stream.getvalue()

            full_path: Path = output_dir / target
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(data)
            self.on_progress.emit(extraction_tracker)

    # The rarfile package does not come with stubs, but is very close to zipfile.
    # Type the structures similarly (for example: namelist() is still list[str], just like in zipfile)
    # Pyright was stub file for it, which may or may not be helpful. It seems to have satisfied the typechecker.
    def _extract_rar(self, archive_file: Path, output_dir: Path, extraction_tracker: ExtractionTracker) -> None:
        with RarFile(archive_file, 'r') as archive_ref:
            archive_items: list[str] = archive_ref.namelist()
            modfile_targets: list[str] = [
                item for item in archive_items
                if RELATIVE_MOD_PATH_PATTERN.search(str(Path(item).parent))
                and not archive_ref.getinfo(item).is_dir()  # pyright: ignore[reportUnknownMemberType]
            ]
            extraction_tracker.current_archive_targets = modfile_targets
            mod_name = archive_file.stem

            for index, target in enumerate(modfile_targets):
                raw_bytes: bytes = archive_ref.read(target)  # pyright: ignore[reportUnknownMemberType]
                extraction_tracker.current_target_index = index
                adjusted_path = self._adjust_modfile_path_for_mgr(target, mod_name)

                output_path: Path = output_dir / adjusted_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(raw_bytes)
                self.on_progress.emit(extraction_tracker)

    def install_archives(self, mod_archives: list[Path], output_dir: Path) -> None:
        if not mod_archives:
            return

        tracker = ExtractionTracker(all_mod_archives = [str(file) for file in mod_archives])
        
        for index, archive in enumerate(mod_archives):
            suffix = archive.suffix.lower()
            tracker.current_archive_index = index
            extractors = {
                SupportedArchiveTypes.ZIP.value: self._extract_zip,
                SupportedArchiveTypes.SEVENZIP.value: self._extract_sevenzip,
                SupportedArchiveTypes.RAR.value: self._extract_rar
            }
            if extractor := extractors.get(suffix):
                extractor(archive, output_dir, tracker)
            else:
                raise ValueError(f'Unsupported archive type: {archive.suffix}')

        self.on_finished.emit()

    def _adjust_modfile_path_for_mgr(self, modfile_path: str, new_parent_dir_name: str) -> str:
        """
        Constructs a new path for the mod, making it more identifiable to MGR by changing the
        modfiles' parent directory name to mirror the original mod archive name.
        """
        pattern_match = RELATIVE_MOD_PATH_PATTERN.search(str(Path(modfile_path).parent))
        if not pattern_match:
            raise InvalidItemStructure(f"Extracting to memory failed; invalid pattern match: {modfile_path}")
        match_groupdict = pattern_match.groupdict()
        new_path = (
            Path(match_groupdict[RelativeModPathKeys.MONSTER_ID_WITH_EM]) /
            match_groupdict[RelativeModPathKeys.VARIANT_ID] /
            new_parent_dir_name / Path(modfile_path).name
        )
        return str(new_path)

            
            