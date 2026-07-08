from enum import StrEnum
import re
# Matches the core mod path segment: em##/##/<mod_dir_name>
# To match a modfile, search against the file's parent directory; the filename
# itself is taken separately (e.g. Path(item).name).
RELATIVE_MOD_PATH_PATTERN: re.Pattern[str] = re.compile(r"(?P<path_core>(?P<monster_id_with_em>em(?P<monster_id>\d+))[\/\\](?P<variant_id>\d+)[\/\\](?P<mod_dir_name>[^\/\\]+))$")
class RelativeModPathKeys(StrEnum):
    PATH_CORE = "path_core"
    MOD_DIR_NAME = "mod_dir_name"
    MONSTER_ID_WITH_EM = "monster_id_with_em"
    MONSTER_ID = "monster_id"
    VARIANT_ID = "variant_id"

# Matches the filename pattern necessary to extract the mod's Nexus ID
NEXUS_METADATA_PATTERN: re.Pattern[str] = re.compile(r"-(?P<nexus_id>\d+)(?:-\d+)+-(?P<nexus_timestamp>\d{10})$")
class NexusMetadataKeys(StrEnum):
    NEXUS_ID = "nexus_id"
    NEXUS_TIMESTAMP = "nexus_timestamp"


