from pathlib import Path
from typing import Self
from PySide6.QtCore import QObject, QThread, Signal, Slot
import loguru

from mgr.configs.models.app_config import AppConfig
from mgr.configs.models.nexus_mod_archive import NexusModArchive
from mgr.configs.services.base_config_service import ConfigService
from mgr.mods.mod_archive_installer import ArchiveExtractor, ExtractionTracker
from mgr.mods.registries.mod_registry import ModRegistry

logger = loguru.logger
    
class ModService(QObject):
    mods_changed: Signal = Signal()

    def __init__(
        self,
        mod_registry: ModRegistry,
        app_config_service: ConfigService[AppConfig],
        nexus_archive_service: ConfigService[NexusModArchive]
    ):
        super().__init__()
        self._mod_registry: ModRegistry = mod_registry
        self._app_config_service: ConfigService[AppConfig] = app_config_service
        self._nexus_archive_service: ConfigService[NexusModArchive] = nexus_archive_service

        self._mgr_mods_source: Path = app_config_service.config.mgr_mods_dir
        self._mhw_mods_source: Path = app_config_service.config.mhw_mods_dir

        self._thread: QThread
        self._archive_extractor: ArchiveExtractor

    @property
    def mgr_mods_dir(self):
        return self._app_config_service.config.mgr_mods_dir
    
    @property
    def mhw_mods_dir(self):
        return self._app_config_service.config.mhw_mods_dir
    
    @property
    def registry(self):
        return self._mod_registry

    @Slot()
    def _on_install_finished(self):
        print("install finished")
        self.load_mods()
        self.mods_changed.emit()
    
    @Slot()
    def _on_install_progress(self, extraction_tracker: ExtractionTracker):
        print(f"Current Archive Progress: {extraction_tracker.current_archive_progress_outof} ({extraction_tracker.current_archive_progress_percent}) ({extraction_tracker.global_archive_progress_percent})")

    @classmethod
    def create(
        cls,
        mod_registry: type[ModRegistry],
        app_config_service: ConfigService[AppConfig],
        nexus_archive_service: ConfigService[NexusModArchive]
    ) -> Self:
        registry = mod_registry(app_config_service, nexus_archive_service)
        registry.load()
        
        return cls(registry, app_config_service, nexus_archive_service)



    def install_mods(self, archive_files: list[Path]):
        self._thread = QThread()
        self._archive_extractor = ArchiveExtractor()
        self._archive_extractor.moveToThread(self._thread)

        self._thread.started.connect(
            lambda: self._archive_extractor.install_archives(archive_files, self.mgr_mods_dir)
        )
        self._archive_extractor.on_finished.connect(self._on_install_finished)
        self._archive_extractor.on_finished.connect(self._thread.quit)
        self._archive_extractor.on_finished.connect(self._archive_extractor.deleteLater)
        self._archive_extractor.on_finished.connect(self._thread.deleteLater)
        self._archive_extractor.on_progress.connect(self._on_install_progress)
        self._thread.start()
    
    def uninstall_mods(self, mod_paths: list[Path]):  # pyright: ignore[reportUnusedParameter]
        pass

    def load_mods(self):
        self._mod_registry.load()    


    