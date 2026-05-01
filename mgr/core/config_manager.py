"""
Provides tools and structures for handling MGR's config file.
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from json import JSONDecodeError
import os
from pathlib import Path
import tempfile
import json
import shutil
from typing import ClassVar
from pydantic import BaseModel, ConfigDict, ValidationError
from mgr.core.constants import MHW_DIR_NAME, MHW_EXE_NAME
from mgr.core.exceptions import ConfigNotInitializedError, CorruptConfigError, FatalConfigError, MissingConfigFileError
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

class AppConfigFields(StrEnum):
    MHW_DIR = "mhw_dir"
    MGR_MODS_DIR = "mgr_mods_dir"
    APPLIED_SEED = "applied_seed"

class AppConfig(BaseModel):
    """Immutable Pydantic model defining MGR's config schema and default values."""
    # We're freezing this model to avoid mutation. Extra keys are also forbidden to prevent corruption.
    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid', frozen=True)

    mhw_dir: Path | None = None
    mgr_mods_dir: Path | None = None
    applied_seed: int | None = None

class IssueCode(Enum):
    MISSING_REQUIRED_VALUE = "missing_required_value"
    PATH_IS_BROKEN = "path_is_broken"
    MISSING_MHW_EXE = "missing_mhw_exe"
    INVALID_MHW_DIR_NAME = "invalid_mhw_dir_name"

class ConfigStatus(Enum):
    IS_DEFAULT = auto()
    IS_VALID = auto()
    IS_INVALID = auto()

@dataclass
class FieldIssue:
    """Holds information about config errors"""
    codes: list[IssueCode]
    key: str
    value: int | str | Path | None
    message: str | None = None

@dataclass
class ConfigValidationReport:
    """Holds information about config errors"""
    config: AppConfig
    status: ConfigStatus
    field_issues: list[FieldIssue]

class ConfigManager:
    """Manages loading, staging, and committing changes to MGR's config file."""

    def __init__(self, config_file: Path):
        self._config_file: Path = config_file
        self._app_config: AppConfig | None = None


    @property
    def config(self) -> AppConfig:
        if not self._app_config:
            raise ConfigNotInitializedError("'config' property accessed before config was initialized.")
        return self._app_config


    def load(self) -> ConfigValidationReport:
        """Loads MGR's config file into memory.
        
        Raises:
            MissingConfigFileError: If a config file is not found at the provided path.
            CorruptConfigError: If the config has somehow become corrupt or contains invalid properties.
            FatalConfigError: If an issue occurs that completely prevents config management.
        """

        logger.info("Loading config from '%s'.", self._config_file)

        try:
            with open(self._config_file, 'r') as config_file:
                app_config = AppConfig.model_validate_json(config_file.read())
        except FileNotFoundError as error:
            raise MissingConfigFileError(f"No config found at '{self._config_file}'.")
        except (PermissionError, MemoryError, OSError) as error:
            raise FatalConfigError(f"Failed to load config from '{self._config_file}' due to system error.") from error
        except (JSONDecodeError, ValidationError) as error:
            raise CorruptConfigError(f"Config file at '{self._config_file}' is corrupt or has invalid structure.") from error
        
        self._app_config = app_config

        config_validation_report = self.validate(self._app_config)
        if not config_validation_report.status == ConfigStatus.IS_VALID:
            logger.debug("Config loaded with field issues.")
        else:
            logger.info(f"Config successfully loaded:\n{app_config.model_dump_json(indent=2)}")

        return config_validation_report


    def _save(self) -> None:
        """Atomically writes config data to the config file."""

        if not self._app_config:
            raise ConfigNotInitializedError("_save() called before config was initialized. Call load() config first.")

        logger.debug("Preparing to save config to file.")
        temp_file: Path | None = None

        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile('w', dir=self._config_file.parent, delete=False, suffix='.temp', encoding='utf-8') as file:
                temp_file = Path(file.name)
                logger.debug("Writing data to temp file '%s'.", temp_file)
                json.dump(self._app_config.model_dump(mode='json'), file, indent=4)
                
                # Flush and sync to avoid Windows problems due to the way it locks open files
                file.flush()
                os.fsync(file.fileno())

            temp_file.replace(self._config_file)
            logger.debug("Save complete. Temp file has replaced config at '%s'", self._config_file)

        except (PermissionError, MemoryError, TypeError, OSError) as error:
            logger.error("Failed to save config to '%s'.", self._config_file)
            raise FatalConfigError(f"Could not save config.") from error
        finally:
            if temp_file and temp_file.exists():
                logger.warning("Deleting temp file at '%s'", temp_file)
                temp_file.unlink(missing_ok=True)


    def update(self, config_changes: AppConfig) -> ConfigValidationReport:
        logger.debug("Attempting config update with the following changes: '%s'", config_changes.model_dump_json(indent=2, exclude_unset=True))

        if not self._app_config:
            raise ConfigNotInitializedError("update() was called before config was initialized. Call load() first.")

        # Dev note: Originally had this statement return an explicit IS_VALID report. Not sure whether that's better
        # or worse than called validate on the global _app_config. I should probably gate it so that it's assumed
        # valid if assigned to the global.
        if config_changes == self._app_config:
            logger.debug("Update skipped: No fields differ from current config.")
            return self.validate(self._app_config)

        # Create a copy of self._app_config and update its fields using model_dump(exclude_unset=True) to filter only
        # for changed fields. model_copy should also utilize deep=True to avoide copying nested object ids.
        updated_config = self._app_config.model_copy(update=config_changes.model_dump(exclude_unset=True), deep=True)
        config_report = self.validate(updated_config)
        if not config_report.status == ConfigStatus.IS_VALID:
            return config_report

        previous_config = self._app_config
        self._app_config = updated_config
        try:
            self._save()
        except FatalConfigError as error:
            self._app_config = previous_config
            raise FatalConfigError("Update failed due to fatal config error.") from error
            
        logger.info("Config updated successfully.")
        return config_report


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
        

    def generate_default_config(self, backup_existing_config: bool = False) -> ConfigValidationReport:
        """Generates a new default config file and overwrites and old configs."""

        logger.info("Generating new default config at '%s'.", self._config_file)

        previous_config = self._app_config
        self._app_config = AppConfig()
        try:
            self._save()
            if backup_existing_config:
                self._backup_existing_config()
        except:
            self._app_config = previous_config
            raise
        
        return ConfigManager.validate(self._app_config)
    
    # Dev note: Might need to pack issue codes into a tuple with message so they can be tied together. Otherwise,
    # cases where a FieldIssue has multiple IssueCode in its code list will make messages hard to craft.
    @staticmethod
    def validate(app_config: AppConfig) -> ConfigValidationReport:
        """Validates an AppConfig instance and collects errors into ConfigValidationReport.
        
        Returns:
            ConfigReport(ConfigStatus, list[FieldProblem] | None): Each FieldProblem object contains a problem report for a single field.
        """
        logger.debug(f"Validating config data: {app_config.model_dump_json(indent=2)}")

        # Return default config matches early so the caller can handle None values and run first-time setup if needed.
        if app_config == AppConfig():
            return ConfigValidationReport(app_config, ConfigStatus.IS_DEFAULT, field_issues=[])

        issues: list[FieldIssue] = []
        for key in AppConfig.model_fields.keys():
            value = getattr(app_config, key)  # pyright: ignore[reportAny]
            codes: list[IssueCode] = []

            match key:
                case AppConfigFields.MHW_DIR:
                    if value is None:
                        codes.append(IssueCode.MISSING_REQUIRED_VALUE)
                    else:
                        if isinstance(value, Path) and not value.exists():
                            codes.append(IssueCode.PATH_IS_BROKEN)
                        if isinstance(value, Path) and not value.name == MHW_DIR_NAME:
                            codes.append(IssueCode.INVALID_MHW_DIR_NAME)
                        if isinstance(value, Path) and not (value / MHW_EXE_NAME).exists():
                            codes.append(IssueCode.MISSING_MHW_EXE)
                case AppConfigFields.MGR_MODS_DIR:
                    if value is None:
                        codes.append(IssueCode.MISSING_REQUIRED_VALUE)
                        continue
                    if isinstance(value, Path) and not value.exists():
                        codes.append(IssueCode.PATH_IS_BROKEN)
                case _:
                    pass

            if codes:
                issues.append(FieldIssue(codes=codes, key=key, value=value))

        # For logging purposes.
        if issues:
            # status = ConfigStatus.IS_INVALID
            details_for_logger: dict[tuple[str, str], list[IssueCode]] = defaultdict(list)
            for field_issue in issues:
                key = field_issue.key
                value = field_issue.value
                for code in field_issue.codes:
                    details_for_logger[(str(key), str(value))].append(code)
            logger.debug(f"Unable to validate config because of the following issues:\n{details_for_logger}")

        return ConfigValidationReport(
            config=app_config,
            status=ConfigStatus.IS_INVALID if issues else ConfigStatus.IS_VALID,
            field_issues=issues
        )
