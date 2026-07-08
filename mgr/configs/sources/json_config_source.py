from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, override

import loguru

from mgr.configs.sources.base_config_source import ConfigSource

logger = loguru.logger


class JsonConfigSource(ConfigSource):
    def __init__(self, json_file: Path):
        self._file: Path = json_file

    @property
    @override
    def path(self) -> Path:
        return self._file
    
    @override
    def load(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        with open(self._file, 'r', encoding='utf-8') as base_ref:
            base_data = json.load(base_ref)
        return base_data

    @override
    def save(self, data: dict[str, Any], overwrite: bool = False) -> None:  # pyright: ignore[reportExplicitAny]
        self._file.parent.mkdir(parents=True, exist_ok=True)

        mode = "w" if overwrite else "x"
        with tempfile.NamedTemporaryFile(mode=mode, dir=self._file.parent, delete=False, suffix='.tmp', encoding='utf-8') as target_ref:
            temp_file = Path(target_ref.name)
            json.dump(data, target_ref, indent=4)
            target_ref.flush()
            os.fsync(target_ref.fileno())
        
        temp_file.replace(self._file)

        if temp_file.exists():
            temp_file.unlink(missing_ok=True)

    @override
    def backup(self, to_dir: Path | None = None) -> None:
        backup_suffix = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak'
        if to_dir is not None:
            if not to_dir.is_dir():
                raise TypeError(f'Not a directory: {to_dir}')
            new_file = to_dir / self._file.name / backup_suffix
        new_file = self._file.with_suffix(backup_suffix)
    
        shutil.copy2(self._file, new_file)
    