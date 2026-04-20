from pathlib import Path
from datetime import datetime
import shutil

def create_timestamped_backup(file_path: Path) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path: Path = file_path.with_suffix(f".{timestamp}.bak")

        try:
            shutil.copy2(file_path, backup_path)
        except OSError as error:
            raise OSError(f"Failed to create file backup (target file: {file_path}) (target backup: {backup_path})") from error

        return backup_path