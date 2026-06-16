from enum import StrEnum

class ManifestState(StrEnum):
    NOT_PARSED = "not_parsed"
    LOADED = "loaded"  # Manifest was successfully loaded from a file
    MISSING = "missing"  # Manifest file not found; could not be loaded
    CORRUPT = "corrupt"  # Manifest was found but was corrupt; could not be loaded

class ModState(StrEnum):
    STAGED = "Staged"  # Mod found in MGR. Not found in MHW.
    DEPLOYED = "Deployed"  # Mod found mod in MGR and connected symlink found in MHW. Likely managed by MGR.
    ORPHANED = "Orphaned"  # Mod not found mod in MGR and broken symlink found in MHW.
    FOREIGN = "Foreign"  # Non-symlink found in MHW, but not in MGR. Likely manual installation by user.

class SupportedArchiveTypes(StrEnum):  
    ZIP = '.zip'
    SEVENZIP = '.7z'
    RAR = '.rar'

class SupportedModfileTypes(StrEnum):
    MOD3 = ".mod3"
    MRL3 = ".mrl3"
    CTC = ".ctc"
    TEX = ".tex"
    TOML = ".toml"