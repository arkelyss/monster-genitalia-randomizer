"""Constants available for use across all of MGR"""
from platformdirs import user_data_dir
from pathlib import Path

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("monster-genitalia-randomizer")
except PackageNotFoundError:
    __version__ = "unknown"

# App information
APP_VERSION: str = __version__

# The current drive's root. On Linux this is /, and on Windows it's almost always C:\
SYSTEM_ROOT: Path = Path(Path.cwd().anchor)
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
APP_ROOT_DIR: Path = Path(__file__).parent.parent
APP_ASSETS_DIR: Path = APP_ROOT_DIR / "assets"
APP_FONTS_DIR: Path = APP_ASSETS_DIR / "fonts"
APP_IMAGES_DIR: Path = APP_ASSETS_DIR / "images"


# Useful MHW information such as directories, filenames, supported file types, and potential installation locations.
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

# MGR base files
APP_CONFIG_DIR = Path('mgr') / 'configs'
APP_CONFIG_FILE = APP_CONFIG_DIR / 'app_config.json'
APP_NEXUS_INDEX_FILE = APP_CONFIG_DIR / 'nexus_index.json'

# User data directories and files.
LOCAL_ENVIRONMENT_DIR = Path(user_data_dir("Monster Genitalia Randomizer"))
LOCAL_MODS_DIR = LOCAL_ENVIRONMENT_DIR / "mods" / "em"
LOCAL_LOG_DIR = LOCAL_ENVIRONMENT_DIR / "logs"
LOCAL_CONFIG_DIR = LOCAL_ENVIRONMENT_DIR / "configs"

LOCAL_APP_CONFIG_FILE = LOCAL_CONFIG_DIR / "app_config.json"
LOCAL_NEXUS_INDEX_FILE = LOCAL_CONFIG_DIR / "nexus_index.json"
LOCAL_LOG_FILE = LOCAL_LOG_DIR / "app_log.log"

# Assets
FONT_FIRLEST_REGULAR: Path = APP_FONTS_DIR / "Firlest-Regular.otf"
PALICO_PNG: Path = APP_IMAGES_DIR / "cat.png"


