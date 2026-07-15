"""Constants available for use across all of MGR"""
from platformdirs import PlatformDirs
from pathlib import Path

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("monster-genitalia-randomizer")
except PackageNotFoundError:
    __version__ = "unknown"


# App information
platform_dirs = PlatformDirs("Monster Genitalia Randomizer")
APP_VERSION: str = __version__

# System Files and Directories
SYSTEM_ROOT: Path = Path(Path.cwd().anchor)
SYSTEM_DOWNLOADS_DIR = platform_dirs.user_downloads_path

# MHW Files and Directories
MHW_DIR_NAME = "Monster Hunter World"
MHW_EXE_NAME = "MonsterHunterWorld.exe"
MHW_MODS_DIR_EXTENSION = Path("nativePC") / "em"

POSSIBLE_MHW_EXE_LOCATIONS: list[Path] = [
    SYSTEM_ROOT / "Program Files (x86)" / "Steam" / "steamapps" / "common" / "Monster Hunter World",
    SYSTEM_ROOT / "SteamLibrary" / "steamapps" / "common" / "Monster Hunter World",
    SYSTEM_ROOT / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam" / "steamapps" / "common" / "Monster Hunter World",
    SYSTEM_ROOT / "snap" / "steam" / "common" / ".local" / "share" / "Steam" / "steamapps" / "common" /"Monster Hunter World",
    *Path(SYSTEM_ROOT / "home").glob("*/.local/share/Steam/steamapps/common/Monster Hunter World"),
    *Path(SYSTEM_ROOT / "home").glob("*/.steam/steam/steamapps/common/Monster Hunter World"),
]

# MGR Files and Directories
APP_ROOT = Path('mgr')

APP_ASSETS_DIR = APP_ROOT / 'assets'
APP_IMAGES_DIR = APP_ASSETS_DIR / 'images'
APP_CONFIG_DIR = APP_ROOT / 'configs'

APP_CONFIG_FILE = APP_CONFIG_DIR / 'app_config.json'
APP_NEXUS_ARCHIVE_FILE = APP_CONFIG_DIR / 'nexus_archive.json'
APP_CHECKMARK_IMAGE = APP_IMAGES_DIR / 'checkmark.png'

# User Files and Directories
USER_DATA_DIR = platform_dirs.user_data_path
USER_MODS_DIR = USER_DATA_DIR / "mods" / "em"
USER_LOG_DIR = USER_DATA_DIR / "logs"
USER_LOG_FILE = USER_LOG_DIR / "app_log.log"
USER_CONFIG_DIR = USER_DATA_DIR / "configs"

USER_APP_CONFIG_FILE = USER_CONFIG_DIR / "app_config.json"
USER_NEXUS_ARCHIVE_FILE = USER_CONFIG_DIR / "nexus_index.json"


