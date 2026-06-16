"""Orchestrates the startup procedures and initialization before starting the GUI"""
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import logging
from PySide6.QtWidgets import QApplication, QDialog
from pydantic import BaseModel, ValidationError
from mgr.configs.models.app_config import AppConfig
from mgr.configs.models.nexus_index import NexusIndex
from mgr.configs.repositories.json_file_repository import JsonFileRepository
from mgr.configs.services.config_service import ConfigService
from mgr.core.app_context import AppContext
from mgr.core.constants import APP_CONFIG_FILE, APP_NEXUS_INDEX_FILE, LOCAL_APP_CONFIG_FILE, LOCAL_LOG_DIR, LOCAL_LOG_FILE, LOCAL_NEXUS_INDEX_FILE
from mgr.gui.main_window import MainWindow

from mgr.gui.themes import LIGHT_THEME, apply_theme
from mgr.mods.mod_service import ModService
from mgr.mods.registry import ModRegistry
from resolve_config import ValidatedInputDialog

logger = logging.getLogger("mgr")

def initialize_logging(debug: bool, log_dir: Path) -> None:
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    log_dir.mkdir(parents = True, exist_ok = True)

    rotating_file_handler = RotatingFileHandler(LOCAL_LOG_FILE, maxBytes=5242880, backupCount=3)
    rotating_file_handler.setLevel(logging.WARNING)
    rotating_file_handler.setFormatter(formatter)
    logger.addHandler(rotating_file_handler)

def service_resolver(service: ConfigService[BaseModel]):
    while True:
        try:
            service.try_validate()
            break
        except ValidationError as err:
            dialog = ValidatedInputDialog(service, err)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                logger.error("Resolver canceled; exiting.")
                sys.exit(1)
            service.update(dialog.patch)

def main():
    initialize_logging(debug = True, log_dir = LOCAL_LOG_DIR)

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(logging.shutdown)
    apply_theme(app, LIGHT_THEME)

    app_config_service = ConfigService(AppConfig, JsonFileRepository(APP_CONFIG_FILE), JsonFileRepository(LOCAL_APP_CONFIG_FILE))
    nexus_config_service = ConfigService(NexusIndex, JsonFileRepository(APP_NEXUS_INDEX_FILE), JsonFileRepository(LOCAL_NEXUS_INDEX_FILE))
    app_config_service.load()
    nexus_config_service.load()

    service_resolver(app_config_service)
    service_resolver(nexus_config_service)


    mod_registry = ModRegistry()
    mod_service = ModService(mod_registry, app_config_service, nexus_config_service)
    mod_service.load()

    app_context = AppContext(app_config_service, nexus_config_service, mod_service)

    window = MainWindow(app_context)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":#
    # run()
    main()

