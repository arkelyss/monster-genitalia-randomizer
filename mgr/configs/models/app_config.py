from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticUseDefault

from mgr.core.constants import LOCAL_MODS_DIR, MHW_DIR_NAME, MHW_EXE_NAME


class AppConfig(BaseModel):
    """The fully-resolved runtime config. Single source of truth."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    mhw_dir: Path = Field(json_schema_extra={"display_name": "MHW Install Location"})
    mgr_mods_dir: Path = Field(
        default=LOCAL_MODS_DIR,
        json_schema_extra={"display_name": "Local Mods Directory"},
    )

    @field_validator('mhw_dir')
    @classmethod
    def mhw_install_check(cls, value: Path):
        if not value.exists():
            raise ValueError(f'Invalid Path: Does not exist ({value})')
        if not value.is_dir():
            raise ValueError(f'Invalid MHW Directory: Not a directory ({value})')
        if value.name != MHW_DIR_NAME:
            raise ValueError(f'Invalid MHW Directory: Expected directory named "{MHW_DIR_NAME}", but got "{value.name}" instead.')
        if MHW_EXE_NAME not in [file.name for file in value.iterdir()]:
            raise ValueError(f'Invalid MHW Directory: "{MHW_EXE_NAME}" not found in "{value}".')
        return value

    @field_validator('mgr_mods_dir', mode = 'before')
    @classmethod
    def overwrite_null(cls, value: Any):  # pyright: ignore[reportExplicitAny]
        if value is None:
            raise PydanticUseDefault()
        return value