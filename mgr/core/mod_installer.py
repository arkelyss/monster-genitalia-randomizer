"""Tools for handling mod installation, including installation scripts, validation methods, and identification protocols"""
from math import exp
import zipfile
import py7zr
from pathlib import Path
import re
import tempfile
import shutil
from typing import Callable
from collections import defaultdict

from mgr.core.constants import FILE_PATH_PATTERN, SUPPORTED_FILE_TYPES, NATIVEPC_EM_PATH, MANIFEST_FILENAME
from mgr.core.constants import FILE_STATUS_INSTALLED
from mgr.core.exceptions import InvalidModPackage, ModAlreadyInstalled, CorruptInstallation, MismatchedFileCount, IdenticalModInstalled

ZIP = ".zip"
SEVENZIP = ".7z"
OVERWRITE = "overwrite"
SKIP = "skip"

class ModInstaller:
    def __init__(self, mod_path: Path):
        self._pattern: str = re.compile(FILE_PATH_PATTERN)
        self.duplicate_behavior: str = SKIP

        self.mod_path = mod_path
        self.mod_name = mod_path.stem
        self.package_type = mod_path.suffix.lower()
        self.valid_files = self._get_valid_file_paths()
        self.installation_map = self._build_installation_map()
        
    def _is_valid_file(self, file_path: Path):
        return (
            file_path.suffix.lower() in SUPPORTED_FILE_TYPES
            and self._pattern.search(str(file_path)) # Insures that the file path contains at least the em/em##/##/mod/ pattern
        )

    def _get_valid_file_paths(self):
        valid_files = []

        if self.package_type == ZIP:
            with zipfile.ZipFile(self.mod_path, 'r') as package:
                valid_files = [
                    Path(path.filename) for path in package.infolist() if not path.is_dir()
                    and self._is_valid_file(Path(path.filename))
                ]

        elif self.package_type == SEVENZIP:
            with py7zr.SevenZipFile(self.mod_path, mode='r') as package:
                valid_files = [
                    Path(path.filename) for path in package.list() if not path.is_directory
                    and self._is_valid_file(Path(path.filename))
                ]
        
        if not valid_files:
            raise InvalidModPackage(f"Bad package structure or no supported mod files found in '{self.mod_name}'")
        
        return valid_files


    def _build_installation_map(self) -> dict[str, list[tuple[Path, Path]]]:
        installation_map: dict[str, list[tuple[Path, Path]]] = defaultdict(list)

        if self.valid_files:
            for path in self.valid_files:
                em_index = path.parts.index("em")
                monster_id, variant_id = path.parts[em_index + 1], path.parts[em_index + 2]
                old_file_path = path
                new_file_path = Path(monster_id) / Path(variant_id) / self.mod_name / path.name

                installation_map[f"{monster_id}/{variant_id}"].append((old_file_path, new_file_path))

        return installation_map

    def _detect_conflicts(self, target_directory: Path, monster_code: Path):
        """
        Detects conflicts between the target directory and mod being installed.
        Raises errors if the target shares identical features (name and files),
        unsupported filetypes, or mismatching number of files.
        """
        found_filenames = [found_path.name for found_path in target_directory.iterdir()]
        expected_filenames = [old_path.name for old_path, _ in self.installation_map[str(monster_code)]]

        # Check to see if any of the found filetypes are unsupported.
        # Unsupported filetypes may indicate corrupt files or invalid mod installations.
        # It could also indicate that MGR contains outdated info about supported filetypes, but this is unlikely.
        if not all(filename.suffix in SUPPORTED_FILE_TYPES for filename in target_directory.iterdir()):
            raise CorruptInstallation(f"A corrupt installation of {self.mod_name} was discovered.")

        # Check to see if the number of found files differs from the number of files being installed.
        # Indicates strange behavior. If the author updates their mod, the name of the mod should have changed by NexusMods.
        # This suggests tampering, but it's impossible to tell which source (the installed mod vs the mod package being installed) was modified.
        # I don't expect this error to ever be raised, it would be very uncommon.
        if not set(found_filenames) & set(expected_filenames):
            found_length, expected_length = len(found_filenames), len(expected_filenames)
            info = "more" if found_length > expected_length else "less"
            raise MismatchedFileCount(f"A previous installation of {self.mod_name} was discovered and contains {found_length} {info} files than expected.")

        # All checks have been cleared, meaning the previously-installed mod is identical to the one being installed.
        raise IdenticalModInstalled(f"{self.mod_name} has already been installed for {monster_code}")
    
    def _install_zip(self, base_path: Path, on_progress: Callable[[str, Path, str], None]):
        with zipfile.ZipFile(self.mod_path, 'r') as package:
            for monster_code, files in self.installation_map.items():
                target_directory = Path(base_path / monster_code / self.mod_name)

                if target_directory.exists():
                    raise ModAlreadyInstalled(f"{self.mod_name} has already been installed for {monster_code}")
                
                target_directory.mkdir(parents=True, exist_ok=True)

                for path_tuple in files:
                    old_file_path, new_file_path = path_tuple
                    full_new_path = base_path / new_file_path
                    full_new_path.write_bytes(package.read(str(old_file_path)))


    def _install_7z(self, base_path: Path, on_progress: Callable[[str, Path, str], None]):
        with tempfile.TemporaryDirectory() as temp:
            with py7zr.SevenZipFile(self.mod_path, mode='r') as package:
                package.extract(targets=[str(file_path) for file_path in self.valid_files], path=temp)
            
            for monster_code, file_paths in self.installation_map.items():
                target_directory = Path(base_path / monster_code / self.mod_name)
                
                if target_directory.exists():
                    self._detect_conflicts(target_directory, monster_code)
                
                target_directory.mkdir(parents=True, exist_ok=True)

                for paths in file_paths:
                    old_file_path, new_file_path = paths
                    full_new_path = base_path / new_file_path
                    shutil.copy(Path(temp) / old_file_path, full_new_path)
                    on_progress(self.mod_name, full_new_path, FILE_STATUS_INSTALLED)

    def install(self, destination: Path, on_progress: Callable[[str, Path, str], None]):
        base_path = Path(destination / NATIVEPC_EM_PATH)

        if self.package_type == ZIP:
            self._install_zip(base_path, on_progress)
        elif self.package_type == SEVENZIP:
            self._install_7z(base_path, on_progress)

