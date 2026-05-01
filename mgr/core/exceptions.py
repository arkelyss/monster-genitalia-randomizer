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

class InvalidConfigPathError(ConfigError):
    DEFAULT_MESSAGE: str = "Config path is invalid."

class ConfigNotInitializedError(ConfigError):
    DEFAULT_MESSAGE: str = "Config not initialized."

############################
# Config Validation Errors #
############################
class ConfigValidationError(ConfigError):
    DEFAULT_MESSAGE: str = "Config validation failed."

class InvalidFieldPathError(ConfigValidationError):
    DEFAULT_MESSAGE: str = "A field's value is an invalid."

    def __init__(self, message: str | None = None, field: str | None = None, path: Path | None = None):
        self.field: str | None = field
        super().__init__(message)

class MissingRequiredFieldError(ConfigValidationError):
    DEFAULT_MESSAGE: str = "A required config field is missing a value."

    def __init__(self, message: str | None = None, field: str | None = None):
        self.field: str | None = field
        super().__init__(message)

class MissingMhwDirPathError(MissingRequiredFieldError):
    DEFAULT_MESSAGE: str = "A required config field is missing a value."

    def __init__(self, message: str | None = None, field: str | None = None):
        self.field: str | None = field
        super().__init__(message)

class MissingMhwExeError(MissingRequiredFieldError):
    DEFAULT_MESSAGE: str = "A required config field is missing a value."

    def __init__(self, message: str | None = None, field: str | None = None):
        self.field: str | None = field
        super().__init__(message)


##############
# Mod Errors #
##############
class ModError(AppError):
    DEFAULT_MESSAGE: str = "A mod error has occurred."

class ManifestError(ModError):
    DEFAULT_MESSAGE: str = "A manifest error has occurred."

class CorruptManifestError(ManifestError):
    DEFAULT_MESSAGE: str = "Manifest file is corrupt."
    




