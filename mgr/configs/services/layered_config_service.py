from typing import Any, override

import loguru
from pydantic import BaseModel

from mgr.configs.helpers.helpers import deep_merge
from mgr.configs.services.base_config_service import ConfigService
from mgr.configs.sources.base_config_source import ConfigSource

logger = loguru.logger

class LayeredConfigService[T: BaseModel](ConfigService[T]):
    def __init__(
        self,
        config_model: type[T],
        base_source: ConfigSource,
        overlay_source: ConfigSource,
        base_data: dict[str, Any],  # pyright: ignore[reportExplicitAny]
        overlay_data: dict[str, Any]  # pyright: ignore[reportExplicitAny]
    ):
        self._base_source: ConfigSource = base_source
        self._overlay_source: ConfigSource = overlay_source
        self._base_cache: dict[str, Any] = base_data  # pyright: ignore[reportExplicitAny]
        self._overlay_cache: dict[str, Any] = overlay_data  # pyright: ignore[reportExplicitAny]
        self._model: type[T] = config_model
        self._config: T | None = None

    @property
    @override
    def config(self) -> T:
        if self._config is None:
            raise ValueError('Config has not been validated. Call validate() first.')
        return self._config

    @property
    @override
    def config_dump(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self.config.model_dump()
    
    @property
    @override
    def cached_base(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self._base_cache

    @property
    @override
    def cached_overlay(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self._overlay_cache

    @property
    @override
    def merged_data(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return deep_merge(self._base_cache, self._overlay_cache)
    
    @property
    @override
    def model_class(self) -> type[T]:
        return self._model

    @classmethod
    def create[U: BaseModel](
        cls,
        config_model: type[U],
        base_source: ConfigSource,
        overlay_source: ConfigSource, 
        create_missing_overlay: bool = True
    ) -> 'LayeredConfigService[U]':

        base_data = base_source.load()
        overlay_data: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]

        try:
            overlay_data = overlay_source.load()
        except FileNotFoundError:
            if not create_missing_overlay:
                raise
            overlay_source.save(overlay_data)

        return LayeredConfigService(config_model, base_source, overlay_source, base_data, overlay_data)
    
    @override
    def update(self, update_data: dict[str, Any]) -> None:  # pyright: ignore[reportExplicitAny]
        updated_overlay = deep_merge(self._overlay_cache, update_data)
        updated_base = deep_merge(self._base_cache, updated_overlay)

        self._try_validation(updated_base)

        self._overlay_source.save(updated_overlay, overwrite=True) 
        self._overlay_cache = updated_overlay

    @override
    def initialize_model(self) -> None:
        return self._try_validation()

    def _try_validation(self, new_config: dict[str, Any] | None = None) -> None:  # pyright: ignore[reportExplicitAny]
        logger.debug('Trying validation')
        data = new_config or self.merged_data
        logger.debug(f'Using data to validate: {data}')
        self._config = self._model.model_validate(data)
        logger.debug(f'Data validated: {data}')

    
