from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import logging
import os
from pathlib import Path
from typing import Any
from uuid import UUID

from mgr.core.constants import MANIFEST_FILE_NAME, NATIVEPC_EM_DIR, SUPPORTED_MOD_TYPES, VALID_MOD_PATH_PATTERN

logger = logging.getLogger(__name__)

class GenitaliaFeatures(Enum):
    UNDEFINED = "undefined"
    SLIT = "slit"
    PENIS = "penis"
    VAGINA = "vagina"
    TESTICLES = "testicles"

class GenitaliaState(Enum):
    UNDEFINED = "undefined"
    ERECT = "erect"
    FLACCID = "flacid"
    DISCHARGE = "discharge"
    GLOW = "glow"

class ModState(Enum):
    UNDETERMINED = "undetermined"
    DEPLOYED = "deployed"
    STAGED = "staged"
    
@dataclass
class ModManifest:
    group_id: int | None = None
    uuid: UUID
    monster_id: str
    variant_id: str

    mod_name: str = ""
    mod_creator: str = ""
    version: str = "0.0.0"

    genitalia_features: GenitaliaFeatures = GenitaliaFeatures.UNDEFINED
    genitalia_state: GenitaliaState = GenitaliaState.UNDEFINED

@dataclass
class LoadedMod():
    monster_id: str = ""
    variant_id: str = ""
    manifest: ModManifest | None = None
    state: ModState = ModState.UNDETERMINED
    mod_dir: Path | None = None
    files: list[str] = field(default_factory=list)


@dataclass
class Mods:
    managed: list[LoadedMod] = field(default_factory=list)
    unmanaged: list[LoadedMod] = field(default_factory=list)

    @property
    def deployed(self):
        return [mod for mod ]

    @property
    def staged(self):


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
        self._load_managed_mods()
        self._load_active_mods()

    def _load_managed_mods(self):
        loaded_mod = LoadedMod()
        valid_files: defaultdict[str, Any] = defaultdict(dict)  # pyright: ignore[reportExplicitAny]
        invalid_files: list[Path] = []
        unexpected_file_dirs: list[Path] = []  # Create a placeholder for valid files in unexpected locations (fringe case)
  
        for dir_name, sub_dirs, file_names in os.walk(self._mgr_mods_dir):
            dir_name = Path(dir_name)
            files = [root_dir / name for name in file_names]
            
            if not path.is_file():
                continue
            if path.suffix not in SUPPORTED_MOD_TYPES:
                logger.debug("File with unsupported type '%s' found at '%s'", path.suffix, path)
                invalid_files.append(path)
                continue
            if not VALID_MOD_PATH_PATTERN.match(str(path)):
                logger.debug("Mod file '%s' discovered in unexpected location at '%s'", path.name, path)
                unexpected_file_dirs.append(path)
                continue
            
            if path.name == MANIFEST_FILE_NAME:
                mod_info["manifest_file"] = path

        if not valid_files:
            return

        if valid_files:
            for parent_dir, files in valid_files.items():
                

                file_names = {path.name for path in files}  # Create set for efficient lookup
                manifest = ModManifest() if not MANIFEST_FILE_NAME in file_names:


                manifest_file = None
                for path in files:
                    if path.name == MANIFEST_FILE_NAME:
                        manifest_file = path
                    


                pattern_match = VALID_MOD_PATH_PATTERN.match(str(path))
                if pattern_match:
                    monster_id, variant_id, mod_name, file_name = pattern_match.groups()
                    loaded_mod = LoadedMod(
                        monster_id=monster_id,
                        variant_id=variant_id,
                        manifest=ModManifest
                        
                    )
                    self._mods.managed.append

            


    def _read_manifest(self, manifest_file: Path) -> ModManifest:




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