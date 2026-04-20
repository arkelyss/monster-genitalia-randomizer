from mgr.core.config_manager import ConfigManager
from mgr.core.exceptions import ConfigError



def validate_corruption(config: ConfigManager):
    if config.load_report.was_corrupt:
        raise ConfigError(
            (
                f"Config file was corrupt and needed to be replaced with a new default config.\n\n"
                f"A backup of the corrupt config has been created at {config.load_report.backup_path}"
            )
        )