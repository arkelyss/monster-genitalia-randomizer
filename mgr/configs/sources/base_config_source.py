from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ConfigSource(ABC):
    @property
    @abstractmethod
    def path(self) -> Path:
        pass

    @abstractmethod
    def load(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @abstractmethod
    def save(self, data: dict[str, Any], overwrite: bool = False) -> None:  # pyright: ignore[reportExplicitAny]
        pass

    @abstractmethod
    def backup(self, to_dir: Path | None = None) -> None:
        pass
