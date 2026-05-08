import logging
from PySide6.QtCore import QObject
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication, QFileDialog, QWizard

from mgr.core.config_schema import ConfigSchema
from mgr.gui.first_time_setup_wizard import FirstTimeSetupWizard

logger = logging.getLogger(__name__)


class InformationRequestGUI():
    def __init__(self, app: QApplication):
        self._app: QApplication = app
        self._active_window: QWindow | None = None

    def request_mhw_dir(self):
        path = QFileDialog.getExistingDirectory(None, "Select MHW Directory")
        return path if path else None