from mgr.configs.models.app_config import AppConfig
from mgr.configs.models.nexus_mod_archive import NexusModArchive
from mgr.configs.services.base_config_service import ConfigService
from mgr.mods.mod_service import ModService
 
 
class AppContext:
    def __init__(self, app_config_service: ConfigService[AppConfig], nexus_database_service: ConfigService[NexusModArchive], mod_service: ModService) -> None:
        self._app_config_service: ConfigService[AppConfig] = app_config_service
        self._nexus_index_service: ConfigService[NexusModArchive] = nexus_database_service
        self._mod_service: ModService = mod_service

    @property
    def config(self):
        return self._app_config_service

    @property
    def mods(self):
        return self._mod_service

    @property
    def nexus_database(self):
        return self._nexus_index_service