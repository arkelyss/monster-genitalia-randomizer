import json
from typing import Any

from pydantic import BaseModel

from mgr.configs.repositories.base_repository import ConfigRepository
import logging

logger = logging.getLogger(__name__)

class ConfigService[T: BaseModel]:
    '''Provides tools for validating, loading, and merging configs.'''
    def __init__(
        self,
        config_model: type[T],
        base_repository: ConfigRepository,
        target_repository: ConfigRepository,
    ):
        self._model: type[T] = config_model
        self._base_repo: ConfigRepository = base_repository
        self._override_repo: ConfigRepository = target_repository

        # Persistance for each layer
        self._base_data: dict[str, Any] = self._base_repo.load()  # pyright: ignore[reportExplicitAny]
        self._override_data: dict[str, Any]  # pyright: ignore[reportExplicitAny]
        self._merged_data: dict[str, Any]  # pyright: ignore[reportExplicitAny]
        self._populated_model: T | None = None

    @property
    def base_data(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self._base_data

    @property
    def target_data(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self._override_data

    @property
    def merged_data(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return self._merged_data

    @property
    def read(self) -> T:
        if self._populated_model is None:
            raise RuntimeError('Attempted to access model before validate() has been called. Call validate() first.')
        return self._populated_model

    @property
    def base_path(self):
        return self._base_repo.get_path()

    @property
    def target_path(self):
        return self._override_repo.get_path()

    @property
    def model(self) -> type[BaseModel]:
        return self._model

    def load(self) -> None:
        override_file_name = self._override_repo.get_path().name
        logger.info('Loading data from %s...', override_file_name)

        try:
            override_data = self._override_repo.load()
        except FileNotFoundError:
            logger.warning('Unable to locate %s; generating default file.', override_file_name)
            override_data = self._override_repo.save({}, overwrite = False)


        merged_data = self._deep_merge(self._base_data, override_data)
        self._override_data = override_data
        self._merged_data = merged_data
        
        logger.info('Success!')
        logger.debug('Data loaded:\n%s', json.dumps(override_data, indent = 4))
    
    def _deep_merge(self, base_data: dict[str, Any], override_data: dict[str, Any]) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        base_file_name = self._base_repo.get_path().name
        override_file_name = self._override_repo.get_path().name

        logger.debug('Overriding data from %s with data from %s to create merge', base_file_name, override_file_name)
        merged = dict(base_data)
        for key, value in override_data.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)  # pyright: ignore[reportUnknownArgumentType]
            else:
                merged[key] = value
        
        logger.debug('Success!')
        return merged

    def try_validate(self, override_patch: dict[str, Any] | None = None) -> T:  # pyright: ignore[reportExplicitAny]
        logger.debug('Attempting to validate override...')
        override_patch = override_patch or {}
        candidate_override = self._deep_merge(self._override_data, override_patch)
        candidate_merge = self._deep_merge(self._base_data, candidate_override)
        populated_model = self._model.model_validate(candidate_merge)
        logger.debug('Success model validate!')
        logger.debug(f'Model looks like this: {populated_model.model_dump_json(indent=2)}')
        self._populated_model = populated_model
        return self._populated_model

    def update(self, patch: dict[str, Any]) -> T:  # pyright: ignore[reportExplicitAny]
        patch = patch or {}
        new_override = self._deep_merge(self._override_data, patch)
        new_merged = self._deep_merge(self._base_data, new_override)
        model = self._model.model_validate(new_merged)  # raises before any I/O

        self._override_repo.save(new_override, overwrite=True)

        self._override_data = new_override
        self._merged_data = new_merged
        self._populated_model = model
        return model
        