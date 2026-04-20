from PyQt6.QtCore import QThread, pyqtSignal
from mgr.core.mod_installer import ModInstaller
from mgr.core.exceptions import InvalidModPackage

from pathlib import Path
from typing import final, override

OPTION_SKIP = "skip"
OPTION_OVERWRITE = "overwrite"
OPTION_CANCEL = "cancel"
OPTION_CONTINUE = "continue"

@final
class ExtractionWorker(QThread):
    """
    Accepts an archive queue (list of paths) and sends each one individually to be installed.
    """

    # Contains information about the extraction process, including initial setup info
    # pyqtSignal(number of archives, step value, extraction progress)
    on_start = pyqtSignal(int, int)
    on_progress = pyqtSignal(str, Path, str)
    on_finished = pyqtSignal(list)
    on_conflict = pyqtSignal(str)

    def __init__(self, package_paths: list[Path], destination: Path):
        super().__init__()
        # Target and invalid package paths
        self.destination: Path = destination
        self.invalid_packages: list[Path] = []

        self.installers: list[ModInstaller] = self._build_installer_queue(package_paths)
        self.total_installers: int = len(self.installers)

        self.total_files: int = sum(len(installer.valid_files) for installer in self.installers)
        self.files_processed: int = 0

    @override
    def run(self):
        self.on_start.emit(self.total_installers, self.total_files)
        if self.installers:
            for installer in self.installers:
                installer.install(self.destination, self._emit_progress)
        self.on_finished.emit(self.invalid_packages)

    def _build_installer_queue(self, package_paths: list[Path]) -> list[ModInstaller]:
        installers: list[ModInstaller] = []
        for path in package_paths:
            try:
                installers.append(ModInstaller(path))
            except InvalidModPackage:
                self.invalid_packages.append(path)
        return installers

    def _emit_progress(self, mod_name: str, file_path: Path, status: str) -> None:
        self.on_progress.emit(mod_name, file_path, status)
            