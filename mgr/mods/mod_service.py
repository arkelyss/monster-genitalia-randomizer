import logging
import os
from pathlib import Path
from typing import Any
from PySide6.QtCore import QObject, QThread, Signal, Slot

from mgr.configs.models.app_config import AppConfig
from mgr.configs.models.nexus_index import NexusIndex
from mgr.configs.services.config_service import ConfigService
from mgr.core.constants import MHW_MODS_DIR_EXTENSION
from mgr.core.re_patterns import MOD_PATH_CORE_PATTERN, NEXUS_DATA_PATTERN, ModPathCoreKeys, NexusDataKeys
from mgr.mods.mod_archive_installer import ArchiveExtractor, ExtractionTracker
from mgr.mods.models.enums import SupportedModfileTypes
from mgr.mods.models.loaded_mod import LoadedMod
from mgr.mods.registry import ModRegistry

logger = logging.getLogger(__name__)
    
class ModService(QObject):
    mods_changed: Signal = Signal()

    def __init__(self, mod_registry: ModRegistry, app_config_service: ConfigService[AppConfig], nexus_index_service: ConfigService[NexusIndex]):
        super().__init__()
        self._mod_registry: ModRegistry = mod_registry
        self._app_config_service: ConfigService[AppConfig] = app_config_service
        self._nexus_index_service: ConfigService[NexusIndex] = nexus_index_service

        self._thread: QThread
        self._archive_extractor: ArchiveExtractor

    @property
    def registry(self) -> ModRegistry:
        return self._mod_registry
    
    @property
    def mhw_mods_dir(self):
        return self._app_config_service.read.mhw_dir / MHW_MODS_DIR_EXTENSION
    
    @property
    def local_mods_dir(self):
        return self._app_config_service.read.mgr_mods_dir

    @property
    def nexus_index(self):
        return self._nexus_index_service.read


    @Slot()
    def _on_install_finished(self):
        print("install finished")
        self.load()
        self.mods_changed.emit()
    
    @Slot()
    def _on_install_progress(self, extraction_tracker: ExtractionTracker):
        print(f"Current Archive Progress: {extraction_tracker.current_archive_progress_outof} ({extraction_tracker.current_archive_progress_percent}) ({extraction_tracker.global_archive_progress_percent})")

    def install_mods(self, archive_items: list[Path]):
        self._thread = QThread()
        self._archive_extractor = ArchiveExtractor()
        self._archive_extractor.moveToThread(self._thread)

        self._thread.started.connect(
            lambda: self._archive_extractor.install_archives(archive_items, self.local_mods_dir)
        )
        self._archive_extractor.on_finished.connect(self._on_install_finished)
        self._archive_extractor.on_finished.connect(self._thread.quit)
        self._archive_extractor.on_finished.connect(self._archive_extractor.deleteLater)
        self._archive_extractor.on_finished.connect(self._thread.deleteLater)
        self._archive_extractor.on_progress.connect(self._on_install_progress)
        self._thread.start()
    
    def uninstall_mods(self, mod_paths: list[Path]):
        pass

    def load(self) -> ModRegistry:
        logger.debug("Loading mods from '%s'...", self.local_mods_dir)
        loaded_mods: list[LoadedMod] = []

        for current_dir, dir_names, file_names in os.walk(self.local_mods_dir):
            relative_path = Path(current_dir).relative_to(self.local_mods_dir)

            core_data = MOD_PATH_CORE_PATTERN.match(str(relative_path))
            core_data = core_data.groupdict() if core_data else {}
            if not core_data:
                continue
            dir_names.clear()

            nexus_data = NEXUS_DATA_PATTERN.search(core_data[ModPathCoreKeys.MOD_DIR_NAME])
            nexus_data = nexus_data.groupdict() if nexus_data is not None else {}

            mod_id = self._to_int(nexus_data.get(NexusDataKeys.NEXUS_ID))
            mod_timestamp = self._to_int(nexus_data.get(NexusDataKeys.NEXUS_TIMESTAMP))

            mod_creator, mod_features, mod_states = self._get_nexus_index_data(mod_id, mod_timestamp)

            name = core_data[ModPathCoreKeys.MOD_DIR_NAME]
            path_core = Path(core_data[ModPathCoreKeys.PATH_CORE])
            monster_id = int(core_data[ModPathCoreKeys.MONSTER_ID])
            variant_id = int(core_data[ModPathCoreKeys.VARIANT_ID])
            combined_id = (monster_id, variant_id)
            full_path = Path(current_dir)
            size = sum((full_path / file).stat().st_size for file in file_names)
            valid_files = [Path(file) for file in file_names if Path(file).suffix in SupportedModfileTypes]
            invalid_files = [Path(file) for file in file_names if Path(file).suffix not in SupportedModfileTypes]

            new_mod = LoadedMod(
                name=name,
                size=size,
                creator=mod_creator,
                path_core=path_core,
                full_path=full_path,
                monster_id=monster_id,
                variant_id=variant_id,
                combined_ids=combined_id,
                valid_files=valid_files,
                invalid_files=invalid_files,
                nexus_id=mod_id,
                nexus_timestamp=mod_id,
                features=mod_features,
                states=mod_states
            )
            
            loaded_mods.append(new_mod)
            
        local_mod_registry = ModRegistry(loaded_mods)
        self._mod_registry = local_mod_registry

        logger.debug("load_mods complete: %d mods loaded.", len(local_mod_registry))
        return local_mod_registry

    def _get_nexus_index_data(
        self,
        mod_id: int,
        mod_timestamp: int) -> tuple[str, dict[str, bool], dict[str, bool]]:
        creator = ''
        features = {}
        states = {}

        if id_data := self.nexus_index.nexus_ids.get(str(mod_id)):
            creator = id_data.creator
            timestamps = id_data.timestamps

            if timestamp_data := timestamps.get(str(mod_timestamp)):
                features = timestamp_data.features
                states = timestamp_data.states
        
        return creator, features, states

    def _to_int(self, value: Any, default: int = 0):  # pyright: ignore[reportExplicitAny]
        if not value:
            return default
        try:
            return int(value)
        except(ValueError, TypeError):
            return default