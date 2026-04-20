from typing import Callable

from PyQt6.QtWidgets import QDialog
from mgr.core.app_context import AppContext
from mgr.core.config_schema import Config
from mgr.core.exceptions import CorruptConfigError, FatalConfigError, FatalContextError, MissingConfigError
from mgr.core.logger import get_logger
from mgr.gui.first_time_setup.first_time_setup_wizard import SetupWizard

logger = get_logger(__name__)

type DialogFactory = Callable[[], QDialog]
type ReportProblem = Callable[[DialogFactory], None]
type StepFunction = Callable[[ReportProblem], None]

class StartupSequence():
    def __init__(self, app_context: AppContext) -> None:
        self._app_context: AppContext = app_context

    # Public API to retrieve steps, which contain their associated functions.
    # These will be used in a QThread as callables to initialize the startup sequence.
    @property
    def steps(self) -> list[StepFunction]:
        return [
            self._step_load_config,
            self._step_verify_mhw_directory,
            self._step_load_mods,
        ]


    # Each step accepts two callables: report_status and report_problem.
    # These are assigned by the caller, most likely part of the GUI.
    # report_status will likely be used to emit signals such as progress messages.
    # report_problem will likely hold a QDialog factory that constructs requests for user input.
    def _step_load_config(self, report_problem: ReportProblem) -> None:
        logger.info("Loading config file...")

        try:
            self._app_context.config_manager.load()
            logger.info("Config successfully loaded.")

        except MissingConfigError as error:
            logger.warning("Config file not found - creating default config...")
            self._app_context.config_manager.create_default_config()
            logger.info("Default config successfully created.")

        except CorruptConfigError as error:
            logger.warning("Config file is corrupt - creating backup.")
            self._app_context.config_manager.backup_config()
            logger.info("Backup created. Generating default config.")
            self._app_context.config_manager.create_default_config()
            logger.info("Default config successfully created.")
            
        except FatalConfigError as error:
            logger.error(f"Fatal config error: {error}")
            raise FatalContextError from error

        if self._app_context.config.run_setup:
            config_updates: Config | None = None

            logger.info("First run detected - launching setup wizard.")

            def _wizard_factory() -> QDialog:
                wizard = SetupWizard()

                wizard.config_updates_available.connect(config_updates)

                return wizard
            report_problem(_wizard_factory)

        

    def _step_verify_mhw_directory(self, report_problem: ReportProblem) -> None:
        pass

    def _step_load_mods(self, report_problem: ReportProblem) -> None:
        pass