from dataclasses import dataclass
from pathlib import Path

from mgr.mods.models.loaded_mod import SymlinkStatus


@dataclass(frozen = True)
class ModRegistryFilters:
    name: str | None = None
    monster_id: int | None = None
    variant_id: int | None = None
    full_path: Path | None = None
    relative_path: Path | None = None
    symlink_status: SymlinkStatus | None = None