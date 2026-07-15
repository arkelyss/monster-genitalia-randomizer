import sys

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog
from pydantic import BaseModel, ValidationError

from mgr.configs.models.app_config import AppConfig
from mgr.configs.models.nexus_mod_archive import NexusModArchive
from mgr.configs.services.base_config_service import ConfigService, ConfigValidationReport
from mgr.configs.services.layered_config_service import LayeredConfigService
from mgr.configs.sources.json_config_source import JsonConfigSource
from mgr.core.app_context import AppContext
from mgr.core.constants import APP_CONFIG_FILE, APP_NEXUS_ARCHIVE_FILE, USER_APP_CONFIG_FILE, USER_NEXUS_ARCHIVE_FILE
from mgr.gui.model_form import ModelForm
from mgr.mods.mod_service import ModService
import loguru

from mgr.mods.registries.mod_registry import ModRegistry

logger = loguru.logger

class AppInitializer(QObject):
    config_validation_errors: Signal = Signal(list[ConfigValidationReport])
    setup_complete: Signal = Signal(AppContext)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
    
    # Dev Note: I am considering moving some of the lower-level state-change logic (like prune_orphaned_mods in mod_service)
    # to run() so that it can easily be seen. This would make orchestration easier, because right now it's difficult to
    # figure out where everything is.
    def run(self) -> AppContext:
        # Dev Note: Objects should instantiate fully, load() should transition states. Refactor later so this
        # philosophy holds true.
        app_config_service = LayeredConfigService.create(
            AppConfig,
            JsonConfigSource(APP_CONFIG_FILE),
            JsonConfigSource(USER_APP_CONFIG_FILE)
        )

        # Dev Note: Using the LayeredConfigService as a standin manager for the database. Will refine later.
        nexus_archive_service = LayeredConfigService.create(
            NexusModArchive,
            JsonConfigSource(APP_NEXUS_ARCHIVE_FILE),
            JsonConfigSource(USER_NEXUS_ARCHIVE_FILE)
        )

        # Use resolve_service_validation_errors to handle logic from this point
        # Using try/except on service.initialize_model() would not allow us to
        # explicitly pass the service itself. The resolver would not be able to use the service
        # for testing.
        self._resolve_service_validation_errors(app_config_service)
        self._resolve_service_validation_errors(nexus_archive_service)

        mod_service = ModService.create(
            ModRegistry,
            app_config_service,
            nexus_archive_service
        )

        app_context = AppContext(app_config_service, nexus_archive_service, mod_service)

        return app_context

    def _resolve_service_validation_errors[U: BaseModel](self, config_service: ConfigService[U]) -> None:
        try:
            config_service.initialize_model()
        except ValidationError as exc:
            form = ModelForm(config_service, exc)
            if form.exec() != QDialog.DialogCode.Accepted:
                logger.critical('User cancelled config validation. Exiting.')
                sys.exit(1)

        logger.debug(f'{config_service.model_class.__name__} validated')