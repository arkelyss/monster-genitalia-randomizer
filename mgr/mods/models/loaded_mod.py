from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

class SymlinkStatus(StrEnum):
    BROKEN = 'broken'
    WORKING = 'working'
    NOT_A_SYMLINK = 'not_a_symlink'
    IGNORED = 'ignored'

# Frozen so that object is hashable.

@dataclass(frozen=True)
class LoadedNexusMetadata:
    creator: str = field(default = 'Unknown', compare = False)
    nexus_id: int = field(default = 0, compare = False)
    nexus_timestamp: int = field(default = 0, compare = False)
    features: dict[str, bool] = field(default_factory=dict, compare=False)
    states: dict[str, bool] = field(default_factory=dict, compare=False)

@dataclass(frozen=True)
class LoadedMod:
    name: str = field(compare = False)
    size: int = field(compare = False)
    full_path: Path # Mods are identified by this. No two mods can share the same path.
    relative_path: Path = field(compare = False)
    monster_id: int = field(compare = False)
    variant_id: int = field(compare = False)

    symlink_status: SymlinkStatus = field(compare = False)

    nexus_metadata: LoadedNexusMetadata = field(compare = False)
    valid_files: list[Path] = field(default_factory=list, compare=False)
    invalid_files: list[Path] = field(default_factory=list, compare=False)