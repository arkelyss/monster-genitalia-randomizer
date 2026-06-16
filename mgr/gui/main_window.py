from pathlib import Path

from PySide6.QtCore import QAbstractItemModel
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMenuBar, QPushButton, QStackedWidget, QStatusBar, QToolBar, QWidget, QMainWindow

from mgr.core.app_context import AppContext
from mgr.core.constants import APP_VERSION
from mgr.gui.mod_item_model import ModItemModel
from mgr.gui.mod_tree_view import ModTreeView

class MainWindow(QMainWindow):
    def __init__(self, app_context: AppContext):
        super().__init__()
        # App Context
        self._app_context: AppContext = app_context

        # Window configuration
        self.setWindowTitle(f"Monster Genitalia Randomizer v{APP_VERSION}")
        self.resize(1300,800)

        # Widget creation
        self._mod_table_model: QAbstractItemModel = ModItemModel(self._app_context)
        self._mod_table_view: ModTreeView = ModTreeView(self._mod_table_model)
        self.stack: QStackedWidget = QStackedWidget()

        # Attribute variables assigned later
        self._status_label: QLabel
        self._install_action: QAction
        self._uninstall_action: QAction

        self._create_actions()
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.setMenuBar(self._build_menubar())
        self.addToolBar(self._build_toolbar())
        self.setCentralWidget(self._build_body())
        self.setStatusBar(self._build_status_bar())

    def _build_status_bar(self) -> QStatusBar:
        status_bar = QStatusBar()
        self._status_label = QLabel("Ready")
        status_bar.addWidget(self._status_label)

        return status_bar

    def _build_menubar(self) -> QMenuBar:
        menubar = QMenuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self._install_action)

        return menubar
    
    def _create_actions(self):
        self._install_action = QAction('Install Mod(s)', self)
        self._uninstall_action = QAction('Uninstall Mod(s)', self)
        self._install_action.setToolTip("Install mod archives")
        

    def _build_toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setFixedHeight(50)
        toolbar.addAction(self._install_action)
        toolbar.addAction(self._uninstall_action)
        
        return toolbar


    def _build_body(self) -> QWidget:
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        # self.stack.addWidget(self._build_blank_widget())
        self.stack.addWidget(self._mod_table_view)
        body_layout.addWidget(self.stack)

        return body

    def _build_blank_widget(self) -> QWidget:
        widget = QWidget()
        widget_layout = QHBoxLayout(widget)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(0)

        return widget

    def _build_navbar_footer(self):
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)

        help_button = QPushButton("(?) Help")

        footer_layout.addWidget(help_button)

        return footer

    def _connect_signals(self):
        self._mod_table_view.mod_archives_dropped.connect(self._on_archives_dropped)
        self._uninstall_action.triggered.connect(self._on_uninstall_triggered)

    def _on_archives_dropped(self, archive_list: list[Path]):
        self._app_context.mod_service.install_mods(archive_list)
    
    def _on_uninstall_triggered(self):
        pass        
