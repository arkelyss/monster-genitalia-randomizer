from abc import ABC, abstractmethod

from mgr.mods.models.loaded_mod import LoadedMod


class ModRepository(ABC):
    @abstractmethod
    def load(self) -> list[LoadedMod]:
        pass