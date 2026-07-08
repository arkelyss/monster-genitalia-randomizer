"""Registry that stores loaded mod details and provides various ways of accessing them."""

from dataclasses import asdict
import os
from pathlib import Path
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget
import loguru

from mgr.configs.models.app_config import AppConfig
from mgr.configs.models.nexus_mod_archive import NexusModArchive
from mgr.configs.services.base_config_service import ConfigService
from mgr.core.re_patterns import NEXUS_METADATA_PATTERN, RELATIVE_MOD_PATH_PATTERN, NexusMetadataKeys, RelativeModPathKeys
from mgr.mods.models.enums import SupportedModfileTypes
from mgr.mods.models.loaded_mod import LoadedMod, LoadedNexusMetadata, SymlinkStatus
from mgr.mods.models.mod_registry_filters import ModRegistryFilters

logger = loguru.logger

class ModRegistry(QObject):
    def __init__(self, app_config_service: ConfigService[AppConfig], nexus_archive_service: ConfigService[NexusModArchive], parent: QWidget | None = None):
        super().__init__(parent)
        self._app_config_service: ConfigService[AppConfig] = app_config_service
        self._nexus_archive_service: ConfigService[NexusModArchive] = nexus_archive_service

        self._mgr_mods: tuple[LoadedMod, ...] = ()
        self._mhw_mods: tuple[LoadedMod, ...] = ()

    @property
    def all_mods(self) -> tuple[LoadedMod, ...]:
        return self._mgr_mods + self._mhw_mods
    
    @property
    def mgr_mods(self) -> tuple[LoadedMod, ...]:
        return self._mgr_mods

    @property
    def mhw_mods(self) -> tuple[LoadedMod, ...]:
        return self._mhw_mods

    @property
    def mgr_mods_dir(self):
        return self._app_config_service.config.mgr_mods_dir

    @property
    def mhw_mods_dir(self):
        return self._app_config_service.config.mhw_mods_dir

    @property
    def deployed(self) -> tuple[LoadedMod, ...]:
        # Collect all MHW mods that have working symlinks
        working_mhw_symlink_mods = self.search_mhw_mods(filters=ModRegistryFilters(symlink_status=SymlinkStatus.WORKING))

        # Resolve all working symlinks into a list of paths
        resolved_symlinks = [mod.full_path.resolve() for mod in working_mhw_symlink_mods]

        # Return a tuple containing any MGR mods that can match their full path to a resolved symlink
        return tuple(mod for mod in self._mgr_mods if mod.full_path in resolved_symlinks)

    @property
    def orphaned(self):
        # Broken symlinks are orphaned
        return self.search_mhw_mods(filters=ModRegistryFilters(symlink_status=SymlinkStatus.BROKEN))

    @property
    def foreign(self):
        # Non-symlink mods inside MHW are foreign mods, likely installed manually by the user
        return self.search_mhw_mods(filters=ModRegistryFilters(symlink_status=SymlinkStatus.NOT_A_SYMLINK))

    def load(self):
        mgr_mods = self._load_mods(self.mgr_mods_dir, ignore_symlinks = True)
        mhw_mods = self._load_mods(self.mhw_mods_dir)
        self._mgr_mods = tuple(mgr_mods)
        self._mhw_mods = tuple(mhw_mods)

    def search_mgr_mods(self, filters: ModRegistryFilters) -> tuple[LoadedMod, ...]:
        return self._search_registry(self._mgr_mods, filters)
    
    def search_mhw_mods(self, filters: ModRegistryFilters) -> tuple[LoadedMod, ...]:
        return self._search_registry(self._mhw_mods, filters)

    def search_all_mods(self, filters: ModRegistryFilters) -> tuple[LoadedMod, ...]:
        return self._search_registry(self.all_mods, filters)
        
    def _search_registry(self, mod_group: tuple[LoadedMod, ...], filters: ModRegistryFilters):
        results = list(mod_group)

        if all(value is None for value in asdict(filters).values()):
            return ()

        if filters.name is not None:
            results = [mod for mod in results if mod.name == filters.name]
        if filters.monster_id is not None:
            results = [mod for mod in results if mod.monster_id == filters.monster_id]
        if filters.variant_id is not None:
            results = [mod for mod in results if mod.variant_id == filters.variant_id]
        if filters.full_path is not None:
            results = [mod for mod in results if mod.full_path == filters.full_path]
        if filters.relative_path is not None:
            results = [mod for mod in results if mod.relative_path == filters.relative_path]
        if filters.symlink_status is not None:
            results = [mod for mod in results if mod.symlink_status == filters.symlink_status]

        return tuple(results)

    def _load_mods(self, mod_dir: Path, ignore_symlinks: bool = False) -> list[LoadedMod]:
        loaded_mods: list[LoadedMod] = []

        for current_dir, dir_names, file_names in os.walk(mod_dir):
            relative_path = Path(current_dir).relative_to(mod_dir)
            
            # If mod is a symlink, get the status
            symlink_status = SymlinkStatus.NOT_A_SYMLINK
            if relative_path.is_symlink():
                if ignore_symlinks:
                    continue
                try:
                    relative_path.stat()
                    symlink_status = SymlinkStatus.WORKING
                except FileNotFoundError:  # FileNotFoundError on a symlink.stat() means the symlink is broken
                    symlink_status = SymlinkStatus.BROKEN

            # Try to match the relative path (eg: em057/00/dir_name)
            if (relative_path_match := RELATIVE_MOD_PATH_PATTERN.match(str(relative_path))) is None:
                continue
            relative_path_dict = relative_path_match.groupdict()

            # Clear subdirectories so os.walk doesn't traverse them
            dir_names.clear()

            # Reference the relative path's re.Match groupdict to get mod information
            name = relative_path_dict[RelativeModPathKeys.MOD_DIR_NAME]
            relative_path = Path(relative_path_dict[RelativeModPathKeys.PATH_CORE])
            monster_id = int(relative_path_dict[RelativeModPathKeys.MONSTER_ID])
            variant_id = int(relative_path_dict[RelativeModPathKeys.VARIANT_ID])
            full_path = Path(current_dir)
            size = sum((full_path / file).stat().st_size for file in file_names)
            valid_files = [Path(file) for file in file_names if Path(file).suffix in SupportedModfileTypes]
            invalid_files = [Path(file) for file in file_names if Path(file).suffix not in SupportedModfileTypes]
            nexus_metadata = self._get_nexus_metadata(name)

            # Instantiate a LoadedMod with the retrieved values
            loaded_mod = LoadedMod(
                name=name,
                size=size,
                relative_path=relative_path,
                full_path=full_path,
                monster_id=monster_id,
                variant_id=variant_id,
                valid_files=valid_files,
                invalid_files=invalid_files,
                symlink_status = symlink_status,
                nexus_metadata = nexus_metadata 
            )
            
            loaded_mods.append(loaded_mod)

        logger.debug("%d mods loaded.", len(loaded_mods))
        return loaded_mods

    def _get_nexus_metadata(self, mod_dir_name: str) -> LoadedNexusMetadata:
        '''Patches a LoadedMod with nexus archive metadata if found'''
        nexus_id = 0
        nexus_timestamp = 0
        mod_creator = 'Unknown'
        mod_features = {}
        mod_states = {}

        if nexus_metadata_match := NEXUS_METADATA_PATTERN.search(mod_dir_name):
            nexus_metadata_dict = nexus_metadata_match.groupdict()
            
            # Use the Nexus ID and timestamp to collect mod metadata from the Nexus Archive
            nexus_id = int(nexus_metadata_dict[NexusMetadataKeys.NEXUS_ID])
            nexus_timestamp = int(nexus_metadata_dict[NexusMetadataKeys.NEXUS_TIMESTAMP])
            if (id_details := self._nexus_archive_service.config.nexus_ids.get(nexus_id)) is not None:
                mod_creator = id_details.creator
                if (timestamp_details := id_details.timestamps.get(nexus_timestamp)) is not None:
                    mod_features = timestamp_details.features
                    mod_states = timestamp_details.states

        return LoadedNexusMetadata(
            nexus_id = nexus_id,
            nexus_timestamp = nexus_timestamp,
            creator = mod_creator,
            features = mod_features,
            states = mod_states
        )