"""Orchestrates the startup procedures and initialization before starting the GUI"""
import argparse
from collections import defaultdict
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import logging
from PySide6.QtWidgets import QApplication, QWizard
from mgr.core.constants import CONFIG_DIR, CONFIG_FILE, LOG_DIR, LOG_FILE, MGR_MODS_DIR, MHW_DIR_NAME, MHW_EXE_NAME, MHW_MODS_DIR_NAME
from mgr.core.app_context import AppContext
from mgr.core.exceptions import CorruptConfigError, MissingConfigFileError
from mgr.gui.main_window import MainWindow

from mgr.core.config_manager import AppConfig, AppConfigFields, ConfigManager, ConfigStatus, ConfigValidationReport, IssueCode
from mgr.core.mod_manager import ModManager
from mgr.gui.first_time_setup_wizard import FirstTimeSetupWizard
from typing import Any, cast

from mgr.gui.notifications.popup_message import PopupInput

logger = logging.getLogger("mgr")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# We need ComfigProblemResolver so we can hold a ConfigManager instance.
# This is primarily because of Signal emissions, such as with FirstTimeSetupWizard.
# Without the ConfigManager instance, the emit callback function has no way of reliably retrieiving it.
# An alternate solution would be passing the manager instance into the wizard, but that would obfuscate flow.

class ConfigValidationResolver:
    def __init__(self, config_report: ConfigValidationReport):
        self._config_report: ConfigValidationReport = config_report

    def run(self) -> AppConfig:
        logger.debug("Attempting to resolve config issues...")
        popup_input = PopupInput()

        while not self._config_report.status == ConfigStatus.IS_VALID:
            if self._config_report.status == ConfigStatus.IS_DEFAULT:
                logger.info("Config is default. Running first time setup.")
                setup_wizard = FirstTimeSetupWizard()
                if setup_wizard.exec() == QWizard.DialogCode.Accepted:
                    config_updates = setup_wizard.wizard_app_config.model_dump(exclude_unset=True)
                    updated_config = self._config_report.config.model_copy(update=config_updates, deep=True)
                    self._config_report = ConfigManager.validate(updated_config)
                    continue
                else:
                    sys.exit(logging.shutdown())

            # Create a dictionary to temporarily hold updates so they can be bulk pushed later.
            # This is done to ensure that pydantic's 'exclude_unset=True' in ConfigManager.update() can correctly identify which
            # fields are newly set.
            update_data: dict[str, Any] = defaultdict(Any)  # pyright: ignore[reportExplicitAny]


            for field_issue in self._config_report.field_issues:
                key = field_issue.key
                value = field_issue.value
                issue_codes = field_issue.codes

                # Precise fixes for specific keys. 
                match key:
                    case AppConfigFields.MHW_DIR:
                        if IssueCode.INVALID_MHW_DIR_NAME in issue_codes:
                            user_input = popup_input.show_popup("Invalid MHW Directory", f"Expected directory name to be {MHW_DIR_NAME}, got {value} instead.")
                            if user_input is not None:
                                update_data[key] = user_input
                        if IssueCode.MISSING_MHW_EXE in issue_codes:
                            user_input = popup_input.show_popup(f"Invalid MHW Directory", f"Could not find {MHW_EXE_NAME} at {value}")
                            if user_input is not None:
                                update_data[key] = user_input
                    case _:
                        pass

                # General fixes for when specific keys don't matter.
                if IssueCode.MISSING_REQUIRED_VALUE in issue_codes:
                    user_input = popup_input.show_popup("Missing Required Value", f"{key} value is {value}. Requires value to proceed.")
                    if user_input is not None:
                        update_data[key] = user_input
                if IssueCode.PATH_IS_BROKEN in issue_codes:
                    user_input = popup_input.show_popup("Broken Path", f"{key} path is broken.")
                    if user_input is not None:
                        update_data[key] = user_input


            updated_config = self._config_report.config.model_copy(update=update_data, deep=True)
            self._config_report = ConfigManager.validate(updated_config)
            
    
        return self._config_report.config

@dataclass
class ArgTypes(argparse.Namespace):
    debug: bool

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        type = bool,
        help = "output debug logger messages"
    )
    args = parser.parse_args()
    return args


def create_dirs(dir_paths: list[Path]) -> None:
    logger.debug("Creating directories:\n%s", "\n".join(str(path) for path in dir_paths))
    for path in dir_paths:
        path.mkdir(exist_ok=True, parents=True)


def main() -> None:
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(logging.shutdown)

    _ = cast(ArgTypes, _parse_args())  # Might use later for passing cli args to startup
    
    create_dirs([LOG_DIR, MGR_MODS_DIR, CONFIG_DIR])

    rotating_file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5242880, backupCount=3)
    rotating_file_handler.setLevel(logging.WARNING)
    rotating_file_handler.setFormatter(formatter)
    logger.addHandler(rotating_file_handler)

    config_manager: ConfigManager = ConfigManager(CONFIG_FILE)
    validation_report: ConfigValidationReport
    
    try:
        validation_report = config_manager.load()
    except MissingConfigFileError:
        validation_report = config_manager.generate_default_config()
    except CorruptConfigError:
        validation_report = config_manager.generate_default_config(backup_existing_config=True)

    app_config = ConfigValidationResolver(validation_report).run()
    config_manager.update(app_config)
    
    mhw_dir = config_manager.config.mhw_dir
    mgr_mods_dir = config_manager.config.mgr_mods_dir
    
    if not mhw_dir:
        raise RuntimeError("Monster Hunter World paths were not resolved before ModManager initialization.")
    if not mgr_mods_dir:
        raise RuntimeError("MGR mod path was not resolved before ModManager initialization.")

    mhw_mods_dir = mhw_dir / MHW_MODS_DIR_NAME
    create_dirs([mhw_mods_dir])

    mod_manager = ModManager(mhw_dir, mhw_mods_dir, mgr_mods_dir)
    app_context = AppContext(config_manager, mod_manager)
 
    window = MainWindow(app_context)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":#
    # run()
    main()

