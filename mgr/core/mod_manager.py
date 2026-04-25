from dataclasses import dataclass
from enum import Enum, StrEnum, auto
import logging
import os
from pathlib import Path
from tomlkit import load
from typing import Any, ClassVar
import uuid

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from mgr.core.constants import MANIFEST_FILE_NAME, MOD_DIR_TREE, SUPPORTED_FILE_TYPES
from mgr.core.exceptions import CorruptManifestError

logger = logging.getLogger(__name__)

class GenitaliaFeatures(StrEnum):
    SLIT = "slit"
    PENIS = "penis"
    VULVA = "vulva"
    TESTICLES = "testicles"

class GenitaliaStates(StrEnum):
    ERECT = "erect"
    DISCHARGING = "discharging"
    GLOWING = "glow"

class ManifestStatus(Enum):
    VALID = auto()
    MISSING = auto()
    CORRUPT = auto()

class ModMetadata(BaseModel):
    version: str = "0.0.0"  # Dev note: For now, 0.0.0 will indicate a default MGR-generated manifest. Change version to signal user-modified manifest.
    description: str | None = None
    creator: str | None = None
    
class ModManifest(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra='allow')
    
    display_name: str | None = None   # Dev note: Name shown in user interfaces?
    mod_uuid: uuid.UUID | None = None

    metadata: ModMetadata = ModMetadata()
    
    genitalia_features: dict[GenitaliaFeatures, bool] = Field(default_factory=lambda: {feature: False for feature in GenitaliaFeatures})
    genitalia_states: dict[GenitaliaStates, bool] = Field(default_factory=lambda: {state: False for state in GenitaliaStates})

    custom_features: dict[str, bool] = Field(default_factory=dict)
    custom_states: dict[str, bool] = Field(default_factory=dict)

class ManifestProblem:



@dataclass
class LoadedMod:
    name: str  # Name of the mod, derived from the archive name at time of extraction.
    mod_uuid: uuid.UUID | None  # UUID exclusive to this particular mod. Should not be left at None.

    managed: bool  # True: Exists inside MGR's mod dir | False: Exists inside MHW's mod folder and not MGR's.
    deployed: bool  # True: Symlink inside MHW mod path points to existing mod in MGR mod folder.

    path: Path  # The mod's actual location.
    deploy_path: Path  # Path to deploy a symlink at.

    files: list[Path] | None  # List the names of valid files in the mod directory.
    invalid_files: list[Path] | None  # List the names of invalid files in the mod directory.
    manifest: ModManifest | None  # The loaded mgr_manifest.toml file (if it exists).
    manifest_status: ManifestStatus

    monster_id: int  # Identifies the target monster's primary species.
    variant_id: int  # Identifies the target monster's species variant.


class ModManager():
    def __init__(self, mhw_dir: Path, mhw_mods_dir: Path, mgr_mods_dir: Path):
        self._mhw_dir: Path = mhw_dir
        self._mhw_mods_dir: Path = mhw_mods_dir
        self._mgr_mods_dir: Path = mgr_mods_dir

        self._all_mods: list[LoadedMod] = []

    @property
    def all_mods(self):
        return self._all_mods

    @property
    def managed_mods(self):
        return [mod for mod in self._all_mods if mod.managed]

    @property
    def foreign_mods(self):
        return [mod for mod in self._all_mods if not mod.managed]

    @property
    def deployed_mods(self):
        return [mod for mod in self._all_mods if mod.deployed]

    @property
    def scan_mods_for_missing_manifests(self)
        return [loaded_mod for loaded_mod in self._all_mods if loaded_mod.manifest_status == ManifestStatus.MISSING]
    def initialize(self):
        mods = self.load_mods()

        missing_manifests = [loaded_mod for loaded_mod in mods if loaded_mod.manifest_status == ManifestStatus.MISSING]



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
                try:
                    manifest = self._load_manifest_file(manifest_file)
                    manifest_status = ManifestStatus.VALID
                except CorruptManifestError:
                    logger.warning("Corrupt manifest at '%s', falling back to defaults.", manifest_file)
                    manifest= ModManifest(display_name=mod_name)
                    manifest_status = ManifestStatus.CORRUPT
            else:
                manifest = ModManifest(display_name=mod_name)
                manifest_status = ManifestStatus.MISSING

            

            mods.append(
                LoadedMod(
                    name = mod_name,
                    mod_uuid = manifest.mod_uuid,
                    managed = True,
                    deployed = deployed,
                    path = current_dir,
                    deploy_path = symlink_in_mhw,
                    files = files,
                    invalid_files = invalid_files,
                    manifest = manifest,
                    manifest_status = manifest_status,
                    monster_id = int(monster_id),
                    variant_id = int(variant_id),
                )
            )

        self._all_mods = mods
        return mods
        

    def _load_manifest_file(self, manifest_file: Path) -> ModManifest:
        try:
            with open(manifest_file, 'r') as file:
                # Explicitly convert to dict for Pydantic
                loaded_data: dict[str, Any] = dict(load(file))  # pyright: ignore[reportExplicitAny]
            validated_manifest = ModManifest.model_validate(loaded_data)
            return validated_manifest
        except ValidationError:
            raise CorruptManifestError()

    def _update_manifest_file(self, changes: ModManifest):
        logger.debug("Attempting manifest update with changes: '%s'", changes.model_dump_json(indent=2, exclude_unset=True))

        if changes == ModManifest():
            logger.debug("Manifest update skipped: No fields differ from current manifest.")
            return

        if not self._config_data:
            raise MissingConfigDataError("update() was called before config was loaded.")

        # The following two lines are very important for data integrity. Without them, the config data would be
        # overwritten with default values from inside our passed object whenever the update() method is called.

        # 1. Extract Explicit Changes
        # Use exclude_unset=True to extract only the fields that were explicitely changed.
        update_data = changes.model_dump(exclude_unset=True)

        # 2. Copy Model and Deep Copy
        # Create a new instance of our current data instead of mutating the original. Update fields with update_data.
        # 'deep=True' ensures that any nested objects are also cloned. Otherwise, they would contain the same memory
        # addresses as their originals, meaning any changes to the copy would affect originals too.
        candidate_config = self._config_data.model_copy(update=update_data, deep=True)
        config_report = self._validate_data(candidate_config)

        if config_report.status == ConfigStatus.INVALID:
            message = "\n".join([f"- {problem.name}: {problem.reason}" for problem in config_report.problems])
            logger.debug("Update rejected. Problems found: '%s'", message)
            return config_report

        previous_data = self._config_data
        self._config_data = candidate_config
        try:
            self._save()
        except FatalConfigError as error:
            self._config_data = previous_data
            raise FatalConfigError("Update failed due to fatal config error.") from error
            
        logger.info("Config updated successfully. Changed fields: '%s'", list(update_data.keys()))
        return ConfigReport(status=ConfigStatus.VALID)

    def _detec_manifest_problems(self, mods: list[LoadedMod]):
        # Dev note: Might need to make this a detect method to return issues for user decisions, rather than silently patching.
        for loaded_mod in mods:
            if loaded_mod.manifest_status == ManifestStatus.VALID:
                continue
            elif loaded_mod.manifest_status == ManifestStatus.MISSING:
                self._generate_default_manifest(loaded_mod.path)
            elif loaded_
            
