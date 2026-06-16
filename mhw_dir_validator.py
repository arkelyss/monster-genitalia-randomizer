from pathlib import Path
from typing import Any

from pydantic import ValidationError

from mgr.core.constants import MHW_DIR_NAME, MHW_EXE_NAME


def validate_mhw_dir(mhw_dir: str) -> str | None:
    mhw_dir_path = Path(mhw_dir)
    if not mhw_dir_path.exists():
        return 'Invalid path; location does not exist.'
    if not mhw_dir_path.is_dir():
        return 'Invalid MHW Directory: The path you provided is not a directory.'
    if mhw_dir_path.name != MHW_DIR_NAME:
        return f'Invalid MHW Directory: Expected directory named {MHW_DIR_NAME}, but got {mhw_dir_path.name} instead.'
    if MHW_EXE_NAME not in [file.name for file in mhw_dir_path.iterdir()]:
        return f'Invalid MHW Directory: Could not find {MHW_EXE_NAME} in given directory.'

def resolve(error: ValidationError) -> dict[str, Any]:
    