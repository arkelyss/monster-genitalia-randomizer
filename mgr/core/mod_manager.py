from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import logging
import os
from pathlib import Path
from typing import Any
import uuid

from mgr.core.constants import MANIFEST_FILE_NAME, MOD_DIR_TREE, SUPPORTED_FILE_TYPES

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
    
@dataclass
class ModManifest:
    mod_uuid: uuid.UUID = field(default_factory=uuid.uuid4)

    display_name: str | None = None
    version: str = "0.0.0"  # Dev note: For now, 0.0.0 will indicate a default MGR-generated manifest. Change version to signal user-modified manifest.
    creator: str | None = None
    description: str | None = None

    genitalia_features: dict[str, bool] = field(default_factory=lambda: {feature.value: False for feature in GenitaliaFeatures})
    genitalia_states: dict[str, bool] = field(default_factory=lambda: {state.value: False for state in GenitaliaStates})

@dataclass
class LoadedMod:
    name: str  # Name of the mod, derived from the archive name at time of extraction.
    mod_uuid: uuid.UUID  # UUID exclusive to this particular mod.

    managed: bool  # True: Exists inside MGR's mod dir | False: Exists inside MHW's mod folder and not MGR's.
    deployed: bool  # True: Symlink inside MHW mod path points to existing mod in MGR mod folder.

    mod_dir: Path  # The mod's actual location.
    deploy_dir: Path  # Path to deploy a symlink at.

    files: list[Path] | None  # List the names of valid files in the mod directory.
    invalid_files: list[Path] | None  # List the names of invalid files in the mod directory.
    manifest: ModManifest | None  # The loaded mgr_manifest.toml file (if it exists).

    monster_id: int  # Identifies the target monster's primary species.
    variant_id: int  # Identifies the target monster's species variant.


class ModManager():
    def __init__(self, mhw_dir: Path, mhw_mods_dir: Path, mgr_mods_dir: Path):
        self._mhw_dir: Path = mhw_dir
        self._mhw_mods_dir: Path = mhw_mods_dir
        self._mgr_mods_dir: Path = mgr_mods_dir

    @property
    def all_mods(self):
        raise NotImplementedError("Logic not yet implemented")

    @property
    def managed_mods(self):
        raise NotImplementedError("Logic not yet implemented")

    @property
    def foreign_mods(self):
        raise NotImplementedError("Logic not yet implemented")

    @property
    def deployed_mods(self):
        raise NotImplementedError("Logic not yet implemented")


    def load_mods(self):
        mods: list[LoadedMod] = []

        for current_dir, _, file_names in os.walk(self._mgr_mods_dir):
            current_dir = Path(current_dir)
            relative_dir = current_dir.relative_to(self._mgr_mods_dir)

            # Checks that the relative path matches em/em##/##/dir_name (valid path for a mod)
            path_match = MOD_DIR_TREE.match(str(relative_dir))
            if not path_match:
                continue

            # The path MGR expects this mod's symlink to be if it's deployed.
            symlink_in_mhw = self._mhw_mods_dir / current_dir.parent / "mod"

            if symlink_in_mhw.is_symlink() and symlink_in_mhw.resolve() == current_dir:
                deployed = True
            else:
                deployed = False
                      
            monster_id, variant_id, mod_name = path_match.groups()
            files = [Path(name) for name in file_names if Path(name).suffix in SUPPORTED_FILE_TYPES]
            invalid_files = [Path(name) for name in file_names if Path(name).suffix not in SUPPORTED_FILE_TYPES]

            manifest_file = current_dir / MANIFEST_FILE_NAME

            if manifest_file.exists():
                manifest = self._read_manifest_file(manifest_file)
            else:
                manifest = ModManifest(
                    display_name=mod_name,
                )

            mods.append(
                LoadedMod(
                    name = mod_name,
                    mod_uuid = ModManifest.mod_uuid,
                    managed = True,
                    deployed = deployed,
                    mod_dir = current_dir,
                    deploy_dir = symlink_in_mhw,
                    files = files,
                    invalid_files = invalid_files,
                    manifest = manifest,
                    monster_id = int(monster_id),
                    variant_id = int(variant_id),
                )
            )

        return mods
        

    def _read_manifest_file(self, manifest_file: Path) -> ModManifest:
        raise NotImplementedError("Logic for loading manifest file not yet implemented")

    def _validate_manifest(self) -> bool:
        # May want to write a more generalized "validate_mod" or something to handle all the validation logic.
        raise NotImplementedError("Validation logic for manifest file has not yet been implemented.")