"""Orchestrates the startup procedures and initialization before starting the GUI"""
import argparse
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import logging
from PySide6.QtWidgets import QApplication, QWizard
from mgr.core.config_schema import ConfigSchema
from mgr.core.constants import CONFIG_DIR, CONFIG_FILE, LOG_DIR, LOG_FILE, MGR_MODS_DIR, MHW_MODS_DIR_NAME
from mgr.core.app_context import AppContext
from mgr.core.exceptions import MissingConfigFileError
from mgr.gui.main_window import MainWindow

from mgr.core.config_manager import ConfigManager, ConfigReport, ConfigStatus, FieldStatus
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
class ConfigProblemResolver:
    def __init__(self):
        self._config_manager: ConfigManager
        self._setup_wizard: FirstTimeSetupWizard = FirstTimeSetupWizard()


    def resolve_problems(self, config_manager: ConfigManager, config_report: ConfigReport):
        while config_report.status == ConfigStatus.INVALID:
            logger.debug("Config problems detected.")
            problems = config_report.problems
            required_field_count = 0
            missing_required_count = 0

            for field_info in ConfigSchema.model_fields.values():
                if isinstance(field_info.json_schema_extra, dict) and field_info.json_schema_extra.get("requires_value"):
                    required_field_count += 1
                    print(f"{required_field_count}")

            for problem in problems:
                if problem.status == FieldStatus.MISSING_REQUIRED_VALUE:
                    missing_required_count += 1
                    print(f"Problems: {missing_required_count}")

            # Create a dictionary to temporarily hold updates so they can be bulk pushed later.
            # This is done to ensure that exclude_unset=True in ConfigManager.update() can correctly identify which
            # fields are newly set.
            temp_config_data: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]

            if missing_required_count == required_field_count:
                logger.info("Running first time setup wizard.")
                setup_wizard = FirstTimeSetupWizard()
                if setup_wizard.exec() == QWizard.DialogCode.Accepted:
                    wizard_config_data: ConfigSchema = setup_wizard.wizard_config_data
                    temp_config_data = wizard_config_data.model_dump()
                else:
                    sys.exit(logging.shutdown())
            
            else:
                popup_input = PopupInput()
                for field_problem in problems:
                    if field_problem.status == FieldStatus.MISSING_REQUIRED_VALUE:
                        result = popup_input.show_popup("Missing Required Value", f"{field_problem.reason}")
                        if result:
                            temp_config_data.setdefault(field_problem.name, result)
                    elif field_problem.status == FieldStatus.INVALID_PATH:
                        result = popup_input.show_popup("Invalid Path", f"{field_problem.reason}")
                        if result:
                            temp_config_data.setdefault(field_problem.name, result)
                    elif field_problem.status == FieldStatus.INVALID_MHW_DIR_NAME:
                        result = popup_input.show_popup("Invalid MHW Directory", f"{field_problem.reason}")
                        if result:
                            temp_config_data.setdefault(field_problem.name, result)
                    elif field_problem.status == FieldStatus.MISSING_MHW_EXE:
                        result = popup_input.show_popup("Missing MHW Exe", f"{field_problem.reason}")
                        if result:
                            temp_config_data.setdefault(field_problem.name, result)
                
            new_config_data = ConfigSchema(**temp_config_data)  # pyright: ignore[reportAny]
            config_report = config_manager.update(new_config_data)


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


def create_dirs(data_dirs: list[Path]) -> None:
    logger.debug("Creating user data directories: '%s'", f"{data_dirs}")
    for path in data_dirs:
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
    config_problem_resolver: ConfigProblemResolver = ConfigProblemResolver()
    
    try:
        config_report: ConfigReport = config_manager.load_config()

        if config_report.status == ConfigStatus.INVALID:
            config_problem_resolver.resolve_problems(config_manager, config_report)
    except MissingConfigFileError:
        config_manager.generate_default_config()
    
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

# def run():
#     app = QApplication(sys.argv)
    
#     window = QWidget()
#     layout = QVBoxLayout(window)
    
#     line_edit = QLineEdit()

#     table = QTableView()
#     model = MyModel()
#     sorting_proxy = QSortFilterProxyModel()
#     sorting_proxy.setSourceModel(model)
#     sorting_proxy.setFilterKeyColumn(0)
#     sorting_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
#     line_edit.textChanged.connect(lambda text: sorting_proxy.setFilterRegularExpression(f"^{re.escape(text)}"))
#     table.setModel(sorting_proxy)
#     table.setSortingEnabled(True)

    
    
#     add_btn = QPushButton("Add Person")
#     remove_btn = QPushButton("Remove Last")
    
#     add_btn.clicked.connect(lambda: model.add_person (["Dave", 38, "Develoeper"]))
#     remove_btn.clicked.connect(model.remove_last)
    
#     layout.addWidget(line_edit)
#     layout.addWidget(table)
#     layout.addWidget(add_btn)
#     layout.addWidget(remove_btn)
    
#     window.show()
#     return app.exec()
        
if __name__ == "__main__":
    # run()
    main()

