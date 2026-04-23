from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import logging
import os
from pathlib import Path
from typing import Any
import uuid

from mgr.core.constants import MANIFEST_FILE_NAME, NATIVEPC_EM_DIR, SUPPORTED_FILE_TYPES, VALID_MOD_PATH_STRUCTURE

logger = logging.getLogger(__name__)

class GenitaliaFeatures(Enum):
    UNDEFINED = "undefined"
    SLIT = "slit"
    PENIS = "penis"
    VAGINA = "vagina"
    TESTICLES = "testicles"

class GenitaliaStates(Enum):
    UNDEFINED = "undefined"
    ERECT = "erect"
    DISCHARGING = "discharging"
    GLOWING = "glow"

class ModState(Enum):
    UNKNOWN = "unkown"
    DEPLOYED = "deployed"
    STAGED = "staged"
    
@dataclass
class ModManifest:
    mod_id: uuid.UUID = field(default_factory=uuid.uuid4)
    group_id: uuid.UUID | None = None

    name: str = ""
    creator: str = ""
    version: str = "0.0.0"

    genitalia_features: dict[str, bool] = field(default_factory=lambda: {feature.value: False for feature in GenitaliaFeatures})
    genitalia_states: dict[str, bool] = field(default_factory=lambda: {feature.value: False for feature in GenitaliaStates})

@dataclass
class LoadedMod():
    dir_id: str
    monster_id: int = -1
    variant_id: int = -1
    manifest: ModManifest | None = None
    state: ModState = ModState.UNKNOWN
    path: Path | None = None
    filenames: list[str] = field(default_factory=list)


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
        self._mgr_mods_dir: Path = mgr_mods_dir / NATIVEPC_EM_DIR

        self._mods: Mods = Mods()

    @property
    def mods(self) -> Mods:
        return self._mods

    def load_mods(self):
        self._load_managed_mods()

    def _load_managed_mods(self):
        for current_dir, sub_dir_names, file_names in os.walk(self._mgr_mods_dir):
            current_dir = Path(current_dir)
            relative_dir = current_dir.relative_to(self._mgr_mods_dir)

            path_match = VALID_MOD_PATH_STRUCTURE.match(str(relative_dir))
            if not path_match:
                continue
                      
            monster_id, variant_id, dir_name = path_match.groups()
            valid_files = [name for name in file_names if Path(name).suffix in SUPPORTED_FILE_TYPES]
            invalid_files = [Path(name) for name in file_names if Path(name).suffix not in SUPPORTED_FILE_TYPES]
            state: ModState = self._check_mod_state()
            manifest_file = current_dir / MANIFEST_FILE_NAME
            manifest = ModManifest()

            if manifest_file.exists():
                manifest = self._read_manifest(manifest_file)

            self._mods.managed.append(
                LoadedMod(
                    dir_id=dir_name,
                    monster_id=int(monster_id),
                    variant_id=int(variant_id),
                    manifest=manifest,
                    state=ModState.UNKNOWN,
                    filenames=valid_files
                )
            )


    def _read_manifest(self, manifest_file: Path) -> ModManifest:
        raise NotImplementedError("Logic for loading manifest file not yet implemented")

    def _check_mod_state(self, mod_dir: Path):
        
        expected_deployed_path = self._mhw_mods_dir




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