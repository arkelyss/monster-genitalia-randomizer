from pathlib import Path
from mgr.mods.models.loaded_mod import LoadedMod


class ModRegistry:
    def __init__(self, loaded_mods: list[LoadedMod] | None = None) -> None:
        self._all_mods: tuple[LoadedMod, ...] = tuple(loaded_mods or ())

    @property
    def all_mods(self) -> tuple[LoadedMod, ...]:
        return self._all_mods

    def by_name(self, name: str) -> tuple[LoadedMod, ...]:
        return tuple(mod for mod in self._all_mods if mod.name == name)

    def by_monster_id(self, monster_id: int) -> tuple[LoadedMod, ...]:
        return tuple(mod for mod in self._all_mods if mod.monster_id == monster_id)

    def by_variant_id(self, variant_id: int) -> tuple[LoadedMod, ...]:
        return tuple(mod for mod in self._all_mods if mod.variant_id == variant_id)

    def by_combined_ids(self, monster_id: int, variant_id: int) -> tuple[LoadedMod, ...]:
        return tuple(
            mod for mod in self._all_mods
            if mod.monster_id == monster_id and mod.variant_id == variant_id
        )

    def by_path(self, path: Path) -> tuple[LoadedMod, ...]:
        return tuple(mod for mod in self._all_mods if mod.full_path == path)

    def __len__(self) -> int:
        return len(self._all_mods)

    def __iter__(self):
        return iter(self._all_mods)