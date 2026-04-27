"""
Provides tools and structures for handling MGR's config file.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from json import JSONDecodeError
import os
from pathlib import Path
import tempfile
import json
import shutil
from textwrap import indent
from pydantic import ValidationError
from mgr.core.constants import MHW_DIR_NAME, MHW_EXE_NAME
from mgr.core.exceptions import CorruptConfigError, FatalConfigError, MissingConfigDataError, MissingConfigFileError
from mgr.core.config_schema import ConfigSchema
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class ConfigStatus(Enum):
    """Config file statuses."""
    VALID = auto()
    INVALID = auto()
    MISSING_REPORT = auto()

class FieldStatus(Enum):
    """Config field statuses for caller handling."""
    MISSING_REQUIRED_VALUE = auto()
    INVALID_PATH = auto()
    INVALID_MHW_DIR_NAME = auto()
    MISSING_MHW_EXE = auto()

@dataclass
class FieldProblem:
    """Container for holding information about the specific field problem."""
    status: FieldStatus
    name: str
    reason: str

@dataclass
class ConfigReport:
    """Container for reporting config and field status after validation."""
    status: ConfigStatus | int
    problems: list[FieldProblem] = field(default_factory=list)


class ConfigManager:
    """Manages loading, staging, and committing changes to MGR's config file."""

    def __init__(self, config_path: Path):
        self._config_file: Path = config_path
        self._config_data: ConfigSchema | None = None


    @property
    def config(self) -> ConfigSchema:
        if self._config_data is None:
            raise MissingConfigDataError("'config' property accessed before load() or creation.")
        return self._config_data


    def load_config(self):
        """Loads MGR's config file into memory.
        
        Raises:
            MissingConfigFileError: If a config file is not found at the provided path.
            CorruptConfigError: If the config has somehow become corrupt or contains invalid properties.
            FatalConfigError: If an issue occurs that completely prevents config management.
        """

        logger.info("Loading config from '%s'.", self._config_file)

        try:
            with open(self._config_file, 'r') as config_file:
                loaded_data = ConfigSchema.model_validate_json(config_file.read())
                print(f"{loaded_data}")
                self._config_data = loaded_data
        except FileNotFoundError as error:
            raise MissingConfigFileError(f"No config found at '{self._config_file}'.")
        except (PermissionError, MemoryError, OSError) as error:
            raise FatalConfigError(f"Failed to load config from '{self._config_file}' due to system error.") from error
        except (JSONDecodeError, ValidationError) as error:
            raise CorruptConfigError(f"Config file at '{self._config_file}' is corrupt or has invalid structure.") from error
        
        config_report = self._validate_data(loaded_data)
        
        if not config_report.status == ConfigStatus.VALID:
            logger.info("Config loaded with errors.")
        else:
            logger.info(f"Config successfully loaded:\n{loaded_data.model_dump_json(indent=2)}")

        return config_report


    def _save(self) -> None:
        """Atomically writes config data to the config file."""

        logger.debug("Preparing to save config data to file.")
        temp_file_path: Path | None = None

        if not self._config_data:
            raise MissingConfigDataError("_save was called before config was loaded.")

        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile('w', dir=self._config_file.parent, delete=False, suffix='.temp', encoding='utf-8') as temp_file:
                temp_file_path = Path(temp_file.name)
                logger.debug("Writing data to temp file '%s'.", temp_file_path)
                json.dump(self._config_data.model_dump(mode='json'), temp_file, indent=4)
                
                # Flush and sync to avoid Windows problems due to the way it locks open files
                temp_file.flush()
                os.fsync(temp_file.fileno())

            temp_file_path.replace(self._config_file)
            logger.debug("Save complete. Temp file has replaced config at '%s'.")
        except (PermissionError, MemoryError, TypeError, OSError) as error:
            logger.error("Failed to save config to '%s'.")
            raise FatalConfigError(f"Could not save config.") from error
        finally:
            if temp_file_path is not None and temp_file_path.exists():
                logger.warning("Temp file '%s' discovered after save attempt. Cleaning up.")
                temp_file_path.unlink(missing_ok=True)


    def update(self, changes: ConfigSchema) -> ConfigReport:
        logger.debug("Attempting config update with changes: '%s'", changes.model_dump_json(indent=2, exclude_unset=True))

        if changes == self._config_data:
            logger.debug("Update skipped: No fields differ from current config.")
            return ConfigReport(status=ConfigStatus.VALID)

        if not self._config_data:
            raise MissingConfigDataError("update() was called before config was loaded.")

        # The following two lines are very important for data integrity. Without them, the config data would be
        # overwritten with default values from inside our passed object whenever the update() method is called.

        # 1. Extract Explicit Changes
        # Use exclude_unset=True to extract only the fields that were explicitely changed.
        update_data = changes.model_dump(exclude_unset=True)

        # 2. Copy Model and Deep Copy
        # Create a new instance of our current data instead of mutating the original. Update fields with update_data.
        # 'deep=True' ensures that any nested objects are also cloned. Otherwise, they would contain the same memory
        # addresses as their originals, meaning any changes to the copy would affect originals too.
        candidate_config = self._config_data.model_copy(update=update_data, deep=True)
        config_report = self._validate_data(candidate_config)

        if config_report.status == ConfigStatus.INVALID:
            message = "\n".join([f"- {problem.name}: {problem.reason}" for problem in config_report.problems])
            logger.debug("Update rejected. Problems found: '%s'", message)
            return config_report

        previous_data = self._config_data
        self._config_data = candidate_config
        try:
            self._save()
        except FatalConfigError as error:
            self._config_data = previous_data
            raise FatalConfigError("Update failed due to fatal config error.") from error
            
        logger.info("Config updated successfully. Changed fields: '%s'", list(update_data.keys()))
        return ConfigReport(status=ConfigStatus.VALID)


    def _backup_existing_config(self, config_file: Path | None = None, destination_dir: Path | None = None) -> None:
        """Creates time-stamped backup of an existing config file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_dir = destination_dir or self._config_file.parent 

        old_config_file = config_file or self._config_file
        new_config_file = Path(destination_dir / old_config_file.name).with_suffix(f".{timestamp}.bak")

        try:
            shutil.copy2(old_config_file, new_config_file)
        except FileNotFoundError as error:
            raise MissingConfigFileError("Could not create backup because config file could not be found.") from error
        except (PermissionError, OSError) as error:
            raise FatalConfigError("Could not create config backup.") from error
        

    def generate_default_config(self, backup_existing_config: bool = False) -> None:
        """Generates a new default config file and overwrites and old configs."""

        logger.info("Generating new default config at '%s'.", self._config_file)

        previous_data = self._config_data
        self._config_data = ConfigSchema()
        try:
            self._save()
            if backup_existing_config:
                self._backup_existing_config()
        except Exception:
            self._config_data = previous_data
            raise
    
    # Validate data explicitly instead of using pydantic field validators so that users can be given the option to
    # fix them. Pydantic field validation would cause hard errors immediately after detection.
    def _validate_data(self, config_data: ConfigSchema) -> ConfigReport:
        """Validates config data and returns a list of problems if it finds any.
        
        Returns:
            ConfigReport(ConfigStatus, list[FieldProblem] | None): Each FieldProblem object contains a problem report for a single field.
        """
        problems: list[FieldProblem] = []

        logger.debug(f"Validating config data: {config_data.model_dump_json(indent=2)}")

        for field_name, field_info in ConfigSchema.model_fields.items():
            current_value = getattr(config_data, field_name)  # pyright: ignore[reportAny]

            match field_info.json_schema_extra:
                case {"requires_value": True} if not current_value:
                    problems.append(
                        FieldProblem(
                            name=field_name,
                            status=FieldStatus.MISSING_REQUIRED_VALUE,
                            reason=f"{field_name} requires a value."
                        )
                    )
                case {"requires_path": True} if isinstance(current_value, Path) and not current_value.exists():
                    problems.append(
                        FieldProblem(
                            name=field_name,
                            status=FieldStatus.INVALID_PATH,
                            reason=f"{field_name} path does not"
                        )
                    )
                case {"is_mhw_dir": True}:
                    if current_value.name != MHW_DIR_NAME:
                        problems.append(
                            FieldProblem(
                                name=field_name,
                                status=FieldStatus.INVALID_MHW_DIR_NAME,
                                reason=(
                                    f"Path in {field_name} appears to lead to invalid MHW directory.\n"
                                    "Expected {MHW_DIR_NAME}, got {current_value.name} instead.\n"
                                    "Ignore if intentional, otherwise something went wrong."
                                )
                            )
                        )
                    if not Path(current_value / MHW_EXE_NAME).exists():
                        problems.append(
                            FieldProblem(
                                name=field_name,
                                status=FieldStatus.MISSING_MHW_EXE,
                                reason=(f"Path in {field_name} leads to invalid MHW directory name."
                                "Expected {MHW_DIR_NAME}, got {current_value.name} instead.")
                            )
                        )
                case _:
                    pass

        logger.debug(f"Invalid config, returning problems: {problems}") if problems else logger.debug("Config data validated.")
        if problems:
            logger.debug(f"Unable to validate config data. Problems found: {problems}")
            config_report = ConfigReport(status=ConfigStatus.INVALID, problems=problems)
            return config_report
        else:
            logger.debug("Config data successfully validated")
            config_report = ConfigReport(status=ConfigStatus.VALID)

        return config_report
