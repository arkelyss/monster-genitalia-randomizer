from typing import final
from PySide6.QtWidgets import QStackedLayout, QVBoxLayout, QWidget, QTabBar, QMainWindow

from mgr.core.app_context import AppContext
from mgr.gui.pages import InstallPage, SettingsPage, UninstallPage, ActiveModsPage

@final
class MainWindow(QMainWindow):
    def __init__(self, app: AppContext):
        super().__init__()
        self.app: AppContext = app

        self.setWindowTitle("MGR Dev Build")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background-color: #2d2d2f;")
        self.setAcceptDrops(True)

        self.tab_bar: QTabBar
        self.stack: QStackedLayout

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        central_container: QWidget = self._build_central_container()
        self.setCentralWidget(central_container)

    def _build_central_container(self) -> QWidget:
        central_container = QWidget()
        central_layout = QVBoxLayout(central_container)

        # Tab bar
        tab_bar = QTabBar()

        tab_bar.addTab("Active Mods")
        tab_bar.addTab("Install")
        tab_bar.addTab("Uninstall")
        tab_bar.addTab("Settings")

        central_layout.addWidget(tab_bar)

        # Tab Pages
        active_mods_page: QWidget = ActiveModsPage()
        install_page: QWidget = InstallPage()
        uninstall_page: QWidget = UninstallPage()
        settings_page: QWidget = SettingsPage()

        # Stack to hold tab pages
        self.stack = QStackedLayout()

        self.stack.addWidget(active_mods_page)
        self.stack.addWidget(install_page)
        self.stack.addWidget(uninstall_page)
        self.stack.addWidget(settings_page)

        central_layout.addLayout(self.stack)

        # Synchronize the tabs with the stack's index
        tab_bar.currentChanged.connect(self.stack.setCurrentIndex)

        return central_container

    def _connect_signals(self):
        pass