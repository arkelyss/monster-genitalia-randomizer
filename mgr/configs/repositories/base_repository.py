from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ConfigRepository(ABC):
    @abstractmethod
    def load(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @abstractmethod
    def save(self, config_data: dict[str, Any], overwrite: bool) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @abstractmethod
    def backup(self) -> None:
        pass

    @abstractmethod
    def get_path(self) -> Path:
        pass