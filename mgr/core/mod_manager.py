from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

from mgr.core.constants import MANIFEST_FILE_NAME, NATIVEPC_EM_DIR, SUPPORTED_MOD_TYPES, VALID_MOD_PATH_PATTERN

logger = logging.getLogger(__name__)

class GenitaliaType(Enum):
    UNDEFINED = "undefined"
    SLIT = "slit"
    PENIS = "penis"
    VAGINA = "vagina"
    TESTICLES = "testicles"

class GenitaliaState(Enum):
    UNDEFINED = "undefined"
    ERECT = "erect"
    FLACID = "flacid"
    DISCHARGE = "discharge"

class MonsterSex(Enum):
    UNDEFINED = "undefined"
    MALE = "male"
    FEMALE = "female"
    INTERSEX = "intersex"
    NULL = "null"

class ModState(Enum):
    UNDEFINED = "undefined"
    INSTALLED = "installed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FOREIGN = "foreign"
    
@dataclass
class ModManifest:
    name: str
    author: str | None
    version: float
    state: ModState

    monster_id: str
    variant_id: str
    files: list[str]

    monster_sex: MonsterSex = MonsterSex.UNDEFINED
    genitalia_type: GenitaliaType = GenitaliaType.UNDEFINED
    genitalia_state: GenitaliaState = GenitaliaState.UNDEFINED

@dataclass
class Mods:
    installed: list[ModManifest] = field(default_factory=list)

    active: list[ModManifest] = field(default_factory=list)
    inactive: list[ModManifest] = field(default_factory=list)
    
    foreign: list[ModManifest] = field(default_factory=list)


class ModManager():
    def __init__(self, mhw_dir: Path, mgr_mods_dir: Path):
        self._mhw_dir: Path = mhw_dir
        self._mhw_mods_dir: Path = mhw_dir / NATIVEPC_EM_DIR
        self._mgr_mods_dir: Path = mgr_mods_dir

        self._mods: Mods = Mods()

    @property
    def mods(self) -> Mods:
        return self._mods

    def load_mods(self):
        self._load_installed_mods()
        self._load_active_mods()

    def _load_installed_mods(self):
        self._mods.installed.clear()

        for path in self._mgr_mods_dir.iterdir():
            if not path.is_file():
                continue
            if path.suffix not in SUPPORTED_MOD_TYPES:
                logger.debug("Invalid file of type '%s' found inside installed mod at '%s'", path.suffix, path.parent)
                continue

            pattern_match = VALID_MOD_PATH_PATTERN.match(str(path))
            if not pattern_match:
                logger.debug("Valid file '%s' discovered at invalid location in '%s'", path.name, path.parent)
                continue

            monster_id, variant_id, mod_name, file_name = pattern_match.groups()

    def _load_active_mods(self):
        self._mods.active.clear()

        for path in self._mhw_mods_dir.iterdir():
            if not path.is_file():
                continue
            if path.suffix not in SUPPORTED_MOD_TYPES:
                logger.debug("Invalid file of type '%s' found inside installed mod at '%s'", path.suffix, path.parent)
                continue
            if not path.name == MANIFEST_FILE_NAME:
                logger.debug("Unexpected '%s' file discovered at '%s' while looking for MGR manifest. Expected '%s', got '%s' instead.", path.suffix, path.parent, MANIFEST_FILE_NAME, path.name)
                continue

            pattern_match = VALID_MOD_PATH_PATTERN.match(str(path))
            if not pattern_match:
                logger.debug("Valid file '%s' discovered at invalid location in '%s'", path.name, path.parent)
                continue

            monster_id, variant_id, mod_name, file_name = pattern_match.groups()

    def _validate_manifest(self) -> bool:
        # May want to write a more generalized "validate_mod" or something to handle all the validation logic.
        raise NotImplementedError("Validation logic for manifest file has not yet been implemented.")

        
                

            

            

            
            


            




    # def load(self, installed_mods_directory: Path, active_mods_directory: Path):
    #     # Add validation or guard later against bad directories
    #     self._installed_mods_directory = installed_mods_directory
    #     self._active_mods_directory = active_mods_directory

    #     valid_installed_files: dict[str, dict[str, dict[str, list[str]]]]
    #     invalid_installed_files: list[Path] = []


    #     for path in installed_mods_directory.iterdir():
    #         if path.is_dir():
    #             continue
    #         if path.suffix not in SUPPORTED_FILE_TYPES:
    #             continue

    #         valid_path = re.search(VALID_FILE_PATH_PATTERN, str(path))
            
    #         if 


            
    #         valid_path = re.search(VALID_FILE_PATH_PATTERN, str(path))


            
    #         if re.search(VALID_FILE_PATH_PATTERN, str(path)):
    #             if path.suffix in SUPPORTED_FILE_TYPES
    #         if path.suffix in SUPPORTED_FILE_TYPES:
    #             if re.search()
    #             expected_path = Path(self._installed_mods_directory / NATIVEPC_EM_PATH / )
    #             if re.search(MOD_PATH_PATTERN, str(path))
                    

    #     installed_mods = {re.search(MOD_PATH_PATTERN, str(Path(path.parent))) for path in installed_mods_directory.iterdir() if path.is_file() and path.suffix in SUPPORTED_FILE_TYPES}
    #     active_mods_valid = {Path(path.parent) for path in active_mods_directory.iterdir() if path.is_file() and path.parent in installed_mods}
    #     active_mods_invalid = 

    # def _discover_installed_mods(self):
    #     installed_mods = {Path(path.parent) for path in self.mods_directory.iterdir() if path.is_file()}

    # def _discover_active_mods(self):
    #     active_mods = {Path(path.parent) for path in self.mods_directory.iterdir() if path.is_file()}