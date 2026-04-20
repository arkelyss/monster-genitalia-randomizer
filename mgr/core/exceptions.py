# Can be used for archives that contain incorrect url elements and/or invalid mod files
# Might branch these two later for more granular errors

from pathlib import Path


class AppError(Exception):
    DEFAULT_MESSAGE: str = "An unexpected error has occurred."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.DEFAULT_MESSAGE)

##################
# General Errors #
##################
class IncompleteSetupError(AppError):
    DEFAULT_MESSAGE: str = "First time setup has not been performed."


#################
# Config Errors #
#################
class ConfigError(AppError):
    DEFAULT_MESSAGE: str = "A configuration error has occurred."

class CorruptConfigError(ConfigError):
    DEFAULT_MESSAGE: str = "Config file is corrupt."

class FatalConfigError(ConfigError):
    DEFAULT_MESSAGE: str = "A fatal config error has occurred."

class MissingConfigFileError(ConfigError):
    DEFAULT_MESSAGE: str = "Config file is missing."

class InvalidPathError(ConfigError):
    DEFAULT_MESSAGE: str = "Config path is invalid."

class MissingConfigDataError(ConfigError):
    DEFAULT_MESSAGE: str = "Config not loaded."

class ConfigValidationError(ConfigError):
    DEFAULT_MESSAGE: str = "Config validation failed."

class ConfigExceptionGroup(ExceptionGroup):
    pass

class MissingRequiredValueError(ConfigValidationError):
    DEFAULT_MESSAGE: str = "A required config field is missing a value."

    def __init__(self, message: str, field: str):
        self.field: str = field
        super().__init__(message)

class InvalidValuePathError(ConfigValidationError):
    DEFAULT_MESSAGE: str = "A field's value is an invalid."

    def __init__(self, message: str, field: str, path: Path):
        self.field: str = field
        super().__init__(message)

class InvalidValueTypeError(ConfigValidationError):
    DEFAULT_MESSAGE: str = "Value was of invalid type."

    def __init__(self, message: str, field: str, path: Path):
        self.field: str = field
        super().__init__(message)



class InvalidMhwDirNameError(ConfigValidationError):
    DEFAULT_MESSAGE: str = "MHW directory name is invalid."
class MhwExeNotFoundError(ConfigValidationError):
    DEFAULT_MESSAGE: str = "MHW exe is invalid or not found."


##############
# Mod Errors #
##############
class ModError(AppError):
    DEFAULT_MESSAGE: str = "A mod error has occurred."
    




