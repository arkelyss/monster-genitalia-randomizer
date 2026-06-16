from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LoadedMod:
    name: str
    size: int = field(compare=False)
    full_path: Path  # identity: the real on-disk location
    path_core: Path = field(compare=False)
    monster_id: int = field(compare=False)
    variant_id: int = field(compare=False)
    combined_ids: tuple[int, int] = field(compare=False)

    creator: str = field(default='Unknown', compare=False)
    nexus_id: int = field(default=0, compare=False)
    nexus_timestamp: int = field(default=0, compare=False)
    valid_files: list[Path] = field(default_factory=list, compare=False)
    invalid_files: list[Path] = field(default_factory=list, compare=False)
    features: dict[str, bool] = field(default_factory=dict, compare=False)
    states: dict[str, bool] = field(default_factory=dict, compare=False)