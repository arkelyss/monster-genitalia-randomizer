from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from mgr.core.constants import DRIVE_ROOT

def request_mgr_directory(parent: QWidget | None = None) -> Path | None:
    chosen_directory: str = QFileDialog.getExistingDirectory(
        parent,
        "MHW Installation Directory",
        str(DRIVE_ROOT),
        QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontResolveSymlinks
    )

    if Path(chosen_directory).exists():
        return Path(chosen_directory)
