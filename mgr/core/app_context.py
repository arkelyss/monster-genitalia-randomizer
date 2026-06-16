"""
Holds the fully-initialised services that MainWindow and other GUI
components need at runtime.
 
AppContext is a plain container. It carries no initialisation logic.
All startup work is performed by StartupRunner, which populates an
AppContext instance before MainWindow is created.
"""
 
from pydantic import BaseModel

from mgr.configs.models.app_config import AppConfig
from mgr.configs.models.nexus_index import NexusIndex
from mgr.configs.services.config_service import ConfigService
from mgr.mods.mod_service import ModService
 
 
class AppContext:
    def __init__(self, app_config_service: ConfigService[AppConfig], nexus_index_service: ConfigService[NexusIndex], mod_service: ModService) -> None:
        self._app_config_service: ConfigService[AppConfig] = app_config_service
        self._nexus_index_service: ConfigService[NexusIndex] = nexus_index_service
        self._mod_service: ModService = mod_service

    @property
    def app_config(self) -> BaseModel:
        return self._app_config_service.read

    @property
    def mod_service(self):
        return self._mod_service