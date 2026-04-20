from pydantic import ConfigDict, PositiveInt, BaseModel, Field
from typing import ClassVar
from pathlib import Path

from mgr.core.constants import MHW_DIR_NAME, MHW_EXE_NAME


class ConfigSchema(BaseModel):
    """Immutable Pydantic model defining MGR's config schema and default values."""
    # We're freezing this model to avoid mutation. Extra keys are also forbidden to avoid corruption.
    model_config: ClassVar[ConfigDict] = ConfigDict(extra='forbid', frozen=True)

    # Default keys, types, and values.
    mhw_dir: Path | None = Field(
        default=None,
        json_schema_extra={
            "requires_value": True,
            "requires_path": True,
            "is_mhw_dir": True,
            "mhw_dir_name": MHW_DIR_NAME,
            "mhw_exe_name": MHW_EXE_NAME
            }
        )
    mods_dir: Path | None = Field(default=None, json_schema_extra={"requires_value": True, "requires_path": True})
    randomized: bool = False
    seed: PositiveInt = 1

    class FieldNames:
        mhw_dir: str = "mhw_dir"
        mods_dir: str = "mods_dir"
        randomized: str = "randomized"
        seed: str = "seed"
