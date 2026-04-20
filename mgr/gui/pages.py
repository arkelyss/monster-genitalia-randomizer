from typing import final
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

from mgr.gui.mod_drop_zone import ModDropZone

@final
class ActiveModsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout: QVBoxLayout = QVBoxLayout(self)

        self._build_ui()

    def _build_ui(self):
        self.main_layout.addWidget(self._build_header())
        self.main_layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget(self)
        header.setLayout(QHBoxLayout())
        return header

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        layout = QHBoxLayout(footer)

        install_button: QPushButton = QPushButton("Install Mods")
        install_button.setDisabled(True)

        layout.addWidget(install_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return footer

@final
class InstallPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self._build_ui()

    def _build_ui(self):
        self.main_layout.addWidget(self._build_header())
        self.main_layout.addWidget(ModDropZone(self))
        self.main_layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget(self)
        header.setLayout(QHBoxLayout())
        return header

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        layout = QHBoxLayout(footer)

        install_button: QPushButton = QPushButton("Install Mods")
        install_button.setDisabled(True)

        layout.addWidget(install_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return footer

@final
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self._build_ui()

    def _build_ui(self):
        self.main_layout.addWidget(self._build_header())
        self.main_layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget(self)
        header.setLayout(QHBoxLayout())
        return header

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        layout = QHBoxLayout(footer)

        install_button: QPushButton = QPushButton("Install Mods")
        install_button.setDisabled(True)

        layout.addWidget(install_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return footer

@final
class UninstallPage(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self._build_ui()

    def _build_ui(self):
        self.main_layout.addWidget(self._build_header())
        self.main_layout.addWidget(self._build_footer())


    def _build_header(self) -> QWidget:
        header = QWidget(self)
        header.setLayout(QHBoxLayout())
        return header

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        layout = QHBoxLayout(footer)

        install_button: QPushButton = QPushButton("Install Mods")
        install_button.setDisabled(True)

        layout.addWidget(install_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return footer