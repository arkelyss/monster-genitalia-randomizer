import sys
import logging
from PySide6.QtWidgets import QApplication

from app_initializer import AppInitializer
from mgr.gui.main_window import MainWindow
from mgr.gui.themes import LIGHT_THEME, apply_theme

import loguru

logger = loguru.logger

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(logging.shutdown)
    apply_theme(app, LIGHT_THEME)

    app_initializer = AppInitializer()

    window = MainWindow(app_initializer)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":#
    # run()
    main()

