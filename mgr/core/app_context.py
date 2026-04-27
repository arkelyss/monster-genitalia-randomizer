"""
Holds the fully-initialised services that MainWindow and other GUI
components need at runtime.
 
AppContext is a plain container. It carries no initialisation logic.
All startup work is performed by StartupRunner, which populates an
AppContext instance before MainWindow is created.
"""
 
from mgr.core.config_manager import ConfigManager
from mgr.core.config_schema import ConfigSchema
from mgr.core.mod_manager import ModManager
 
 
class AppContext:
    def __init__(self, config_manager: ConfigManager, mod_manager: ModManager) -> None:
        self._config_manager: ConfigManager = config_manager
        self._mod_manager: ModManager = mod_manager
 
    @property
    def config(self) -> ConfigSchema:
        return self._config_manager.config

    @property
    def mods(self):
        return self._mod_manager.all_mods