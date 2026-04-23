"""Constants available for use across all of MGR"""

from platformdirs import user_data_dir
from pathlib import Path
import re


# The current drive's root. On Linux this is /, and on Windows it's almost always C:\
SYSTEM_ROOT: Path = Path(Path.cwd().anchor)
APP_NAME = "Monster Genitalia Randomizer"


# Useful MHW information such as directories, filenames, and potential installation locations.
MHW_DIR_NAME = "Monster Hunter World"
MHW_EXE_NAME = "MonsterHunterWorld.exe"

NATIVEPC_DIR_NAME = "nativePC"
EM_DIR_NAME = "em"
NATIVEPC_EM_DIR = Path(NATIVEPC_DIR_NAME) / EM_DIR_NAME

POSSIBLE_MHW_INSTALL_DIRS: list[Path] = [
    Path(SYSTEM_ROOT / "Program Files (x86)" / "Steam" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / "SteamLibrary" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / ".local" / "share" / "Steam" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / "snap" / "steam" / "common" / ".local" / "share" / "Steam" / "steamapps" / "common" /" Monster Hunter World")
]


# User data directories and filenames.
USER_DATA_DIR = Path(user_data_dir(APP_NAME))

LOG_FILE_NAME = "mgr.log"
LOG_DIR = USER_DATA_DIR / "logs"
LOG_FILE = LOG_DIR / LOG_FILE_NAME

CONFIG_FILE_NAME = "config.json"
CONFIG_DIR = USER_DATA_DIR / "configs"
CONFIG_FILE = CONFIG_DIR / CONFIG_FILE_NAME

MANIFEST_FILE_NAME = "mgr_manifest.toml"

MGR_MODS_DIR = USER_DATA_DIR / "mods"


# MGR-specific helpers such as supported archive/mod suffixes and regex path validation patterns, 
SUPPORTED_ARCHIVE_TYPES: list[str] = [".zip", ".7z"]
SUPPORTED_FILE_TYPES: list[str] = [".mod3", ".mrl3", ".ctc", ".tex", ".toml"]


# Matches the following pattern: em/em##/##/dirname/filename.suffix
# Use '?P<>' so match.groupdict() can be used later for easy dictionary population of directory structures.
VALID_MOD_PATH_STRUCTURE: re.Pattern[str] = re.compile(r"^em(\d+)[/\\](\d+)[/\\]([^/\\]+)$")
