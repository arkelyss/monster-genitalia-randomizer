from datetime import datetime
import json
import logging
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, override

from mgr.configs.repositories.base_repository import ConfigRepository

logger = logging.getLogger(__name__)


class JsonFileRepository(ConfigRepository):
    def __init__(self, json_config_file: Path):
        self._json_config_file: Path = json_config_file
    
    @override
    def load(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        with open(self._json_config_file, 'r', encoding='utf-8') as config_ref:
            loaded_config = json.load(config_ref)
            return loaded_config
    @override
    def save(self, config_data: dict[str, Any], overwrite: bool = False) -> None:  # pyright: ignore[reportExplicitAny]
        self._json_config_file.parent.mkdir(parents=True, exist_ok=True)

        mode = "w" if overwrite else "x"
        with tempfile.NamedTemporaryFile(mode=mode, dir=self._json_config_file.parent, delete=False, suffix='.tmp', encoding='utf-8') as file:
            temp_file = Path(file.name)
            json.dump(config_data, file, indent=4)
            file.flush()
            os.fsync(file.fileno())
        
        temp_file.replace(self._json_config_file)

        if temp_file.exists():
            temp_file.unlink(missing_ok=True)

    @override
    def backup(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._json_config_file.with_suffix(f".{timestamp}.bak")
    
        shutil.copy2(self._json_config_file, backup_path)

    @override
    def get_path(self) -> Path:
        return self._json_config_file
    