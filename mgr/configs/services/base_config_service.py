from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

@dataclass(frozen=True, slots=True)
class FieldError:
    location: tuple[str | int, ...]
    field_name: str
    field_value: Any  # pyright: ignore[reportExplicitAny]
    message: str

class ConfigService[T: BaseModel](ABC):
    @property
    @abstractmethod
    def config(self) -> T:
        pass

    @property
    @abstractmethod
    def config_dump(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @property
    @abstractmethod
    def model_class(self) -> type[T]:
        pass

    @property
    @abstractmethod
    def cached_base(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @property
    @abstractmethod
    def cached_overlay(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @property
    @abstractmethod
    def merged_data(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        pass

    @abstractmethod
    def update(self, update_data: dict[str, Any]) -> None:  # pyright: ignore[reportExplicitAny]
        pass

    @abstractmethod
    def initialize_model(self) -> None:
        pass

@dataclass
class ConfigValidationReport:
    service: ConfigService[BaseModel]
    config_data: dict[str, Any]  # pyright: ignore[reportExplicitAny]
    field_errors: list[FieldError]
