import sys
import logging
from PySide6.QtWidgets import QApplication

from app_setup import AppSetup
from mgr.gui.main_window import MainWindow
from mgr.gui.themes import LIGHT_THEME, apply_theme

import loguru

logger = loguru.logger

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(logging.shutdown)
    apply_theme(app, LIGHT_THEME)

    app_setup = AppSetup()

    window = MainWindow(app_setup)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":#
    # run()
    main()

