import copy
from typing import Any

import loguru
from pydantic import ValidationError

from mgr.configs.services.base_config_service import FieldError

logger = loguru.logger

def deep_merge(base_data: dict[str, Any], overlay_data: dict[str, Any]) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
    '''Deeply merge target data into base data'''
    result = copy.deepcopy(base_data)
    for key, value in overlay_data.items():
        existing = result.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            result[key] = deep_merge(existing, value)  # pyright: ignore[reportUnknownArgumentType]
        else:
            result[key] = copy.deepcopy(value)
    return result

def build_field_errors(validation_error: ValidationError) -> list[FieldError]:
    field_errors: list[FieldError] = []
    for error in validation_error.errors():
        loc = error['loc']
        field_errors.append(
            FieldError(
                location=loc,
                field_name=str(loc[-1]) if loc else '',
                field_value=error['input'],
                message=error['msg']
            )
        )
    return field_errors