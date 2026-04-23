"""Constants available for use across all of MGR"""

from platformdirs import user_data_dir
from pathlib import Path
import re


# The current drive's root. On Linux this is /, and on Windows it's almost always C:\
SYSTEM_ROOT: Path = Path(Path.cwd().anchor)


# Useful MHW information such as directories, filenames, supported file types, and potential installation locations.
MHW_DIR_NAME = "Monster Hunter World"
MHW_EXE_NAME = "MonsterHunterWorld.exe"
MHW_MODS_DIR_NAME = "nativePC"
MANIFEST_FILE_NAME = "mgr_manifest.toml"
SUPPORTED_ARCHIVE_TYPES: list[str] = [".zip", ".7z"]
SUPPORTED_FILE_TYPES: list[str] = [".mod3", ".mrl3", ".ctc", ".tex", ".toml"]

POSSIBLE_MHW_INSTALL_DIRS: list[Path] = [
    Path(SYSTEM_ROOT / "Program Files (x86)" / "Steam" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / "SteamLibrary" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / ".local" / "share" / "Steam" / "steamapps" / "common" / "Monster Hunter World"),
    Path(SYSTEM_ROOT / "snap" / "steam" / "common" / ".local" / "share" / "Steam" / "steamapps" / "common" /" Monster Hunter World")
]


# User data directories and filenames.
MGR_USER_DATA_DIR = Path(user_data_dir("Monster Genitalia Randomizer"))

MGR_MODS_DIR = MGR_USER_DATA_DIR / "mods"

LOG_DIR = MGR_USER_DATA_DIR / "logs"
LOG_FILE_NAME = "mgr.log"
LOG_FILE = LOG_DIR / LOG_FILE_NAME

CONFIG_FILE_NAME = "config.json"
CONFIG_DIR = MGR_USER_DATA_DIR / "configs"
CONFIG_FILE = CONFIG_DIR / CONFIG_FILE_NAME


# Matches the following pattern: em/em##/##/dirname/filename.suffix
# Use '?P<>' so match.groupdict() can be used later for easy dictionary population of directory structures.
MOD_DIR_TREE: re.Pattern[str] = re.compile(r"^em(\d+)[/\\](\d+)[/\\]([^/\\]+)$")
