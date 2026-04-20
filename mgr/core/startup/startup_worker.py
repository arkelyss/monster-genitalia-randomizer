from PySide6.QtCore import QObject
from mgr.core.mod_installer import ModInstaller

from pathlib import Path
from typing import final, override

class StartupWorker(QObject):
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
            