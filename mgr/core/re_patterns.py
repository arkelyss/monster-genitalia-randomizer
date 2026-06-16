from enum import StrEnum
import re

class ModPathCoreKeys(StrEnum):
    PATH_CORE = "path_core"
    MOD_DIR_NAME = "mod_dir_name"
    EM_MONSTER_ID = "em_monster_id"
    MONSTER_ID = "monster_id"
    VARIANT_ID = "variant_id"

class NexusDataKeys(StrEnum):
    NEXUS_ID = "nexus_id"
    NEXUS_TIMESTAMP = "nexus_timestamp"

# Matches the core mod path segment: em##/##/<mod_dir_name>
# To match a modfile, search against the file's parent directory; the filename
# itself is taken separately (e.g. Path(item).name).
MOD_PATH_CORE_PATTERN: re.Pattern[str] = re.compile(r"(?P<path_core>(?P<em_monster_id>em(?P<monster_id>\d+))[\/\\](?P<variant_id>\d+)[\/\\](?P<mod_dir_name>[^\/\\]+))$")

# Matches the filename pattern necessary to extract the mod's Nexus ID
NEXUS_DATA_PATTERN: re.Pattern[str] = re.compile(r"-(?P<nexus_id>\d+)(?:-\d+)+-(?P<nexus_timestamp>\d{10})$")



