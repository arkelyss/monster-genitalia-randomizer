import logging
from pathlib import Path
from typing import override
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QFileDialog, QHBoxLayout, QPushButton, QSizePolicy, QWidget, QWizard, QWizardPage, QLabel, QLineEdit, QVBoxLayout
from PySide6.QtCore import Qt

from mgr.core.config_manager import AppConfig
from mgr.core.constants import MHW_EXE_NAME, MGR_MODS_DIR, POSSIBLE_MHW_INSTALL_DIRS

logger = logging.getLogger(__name__)
print(f"Logger name: {logger.name}")

class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        message = QLabel(
                "Welcome to the MGR setup wizard!\n\n" +
                "MGR needs extra information to run. This includes the location of your Monster Hunter World installation," +
                "mod preferences, and other customizable details."
        )
        message.setWordWrap(True)

        layout = QHBoxLayout(self)

        left_box = QWidget()
        left_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_box.setFixedWidth(200)
        left_box.setStyleSheet("background-color: orange;")
        _ = QVBoxLayout(left_box)
        
        right_box = QWidget()
        right_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_box_layout = QVBoxLayout(right_box)
        right_box_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_box_layout.addWidget(message)

        layout.addWidget(left_box)
        layout.addWidget(right_box)


class MHWLocationPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("MHW Location")
        self.setSubTitle("Please input the location of your MHW installation directory.")

        self.mhw_dir_input: QLineEdit = QLineEdit()
        detected_mhw = [path for path in POSSIBLE_MHW_INSTALL_DIRS if path.exists()]
        self.mhw_location_match: str = str(detected_mhw[0]) if detected_mhw else ""
        self.mhw_dir_input.setPlaceholderText(self.mhw_location_match)
        self.browse_button: QPushButton = QPushButton("Browse")

        self.status_label: QLabel = QLabel()
        self.status_label.setMargin(5)

        self.registerField("wizard_mhw_dir*", self.mhw_dir_input)

        message_label = QLabel("MGR needs to know where your Monster Hunter World installation is located.")
        message_label.setWordWrap(True)

        input_label = QLabel("MHW Location:")

        input_layout = QHBoxLayout()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.mhw_dir_input)
        input_layout.addWidget(self.browse_button)

        layout = QVBoxLayout(self)
        layout.addWidget(message_label)

        layout.addSpacing(100)

        layout.addLayout(input_layout)
        layout.addWidget(self.status_label)

        self.browse_button.clicked.connect(self._get_mhw_directory)
        self.mhw_dir_input.textChanged.connect(self._validate_mhw_dir)

    def _get_mhw_directory(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Select MHW Directory",
            self.mhw_location_match,
            options = QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.mhw_dir_input.setText(path)

    def _validate_mhw_dir(self):
        candidate_path = Path(self.mhw_dir_input.text())

        is_valid = candidate_path.is_dir() and Path(candidate_path / MHW_EXE_NAME).exists()
        print("Path entered is valid?: '%s'", is_valid)
        logger.debug("Path entered is valid?: '%s'", is_valid)

        if is_valid:
            self.status_label.setText("✔ Valid MHW location")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        elif not candidate_path:
            self.status_label.setText("Please select or input a directory")
            self.status_label.setStyleSheet("color: gray;")
        else:
            self.status_label.setText("✘ Invalid MHW location (MonsterHunterWorld.exe not found)")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    @override
    def isComplete(self) -> bool:
        path = Path(self.mhw_dir_input.text())
        return path.is_dir() and Path(path / MHW_EXE_NAME).exists()

class ModsLocationPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Mods Location")
        self.setSubTitle("Customize where mods are stored.")

        self.mods_dir_input: QLineEdit = QLineEdit()
        self.mods_dir_input.setPlaceholderText(str(MGR_MODS_DIR))
        self.mods_dir_input.setVisible(False)
        self.browse_button: QPushButton = QPushButton("Browse")
        self.browse_button.setVisible(False)

        self.status_label: QLabel = QLabel()
        self.status_label.setVisible(False)
        self.status_label.setMargin(5)

        self.custom_mods_dir_checkbox: QCheckBox = QCheckBox("Choose custom location")

        self.registerField("wizard_mods_dir*", self.mods_dir_input)
        self.registerField("custom_mods_dir_checkbox", self.custom_mods_dir_checkbox)

        message_label = QLabel(
            f"By default, MGR stores mods in a specialized directory located at {MGR_MODS_DIR}. " +
            "This can be changed below, but it's not recommended unless you know what you're doing."
        )
        message_label.setWordWrap(True)

        input_label = QLabel("Mods Location:")
        input_label.setVisible(False)

        input_layout = QHBoxLayout()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.mods_dir_input)
        input_layout.addWidget(self.browse_button)

        layout = QVBoxLayout(self)
        layout.addWidget(message_label)

        layout.addSpacing(100)

        layout.addWidget(self.custom_mods_dir_checkbox)

        layout.addSpacing(20)

        layout.addLayout(input_layout)
        layout.addWidget(self.status_label)

        self.custom_mods_dir_checkbox.toggled.connect(lambda: self.completeChanged.emit())
        self.custom_mods_dir_checkbox.toggled.connect(self.mods_dir_input.setVisible)
        self.custom_mods_dir_checkbox.toggled.connect(self.browse_button.setVisible)
        self.custom_mods_dir_checkbox.toggled.connect(input_label.setVisible)
        self.custom_mods_dir_checkbox.toggled.connect(self.status_label.setVisible)

        self.browse_button.clicked.connect(self._get_directory)
        self.mods_dir_input.textChanged.connect(self._validate_dir)

    def _get_directory(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Select MHW Directory",
            options = QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.mods_dir_input.setText(path)

    def _validate_dir(self):
        raw_input = self.mods_dir_input.text()
        candidate_path = Path(self.mods_dir_input.text())

        is_valid = raw_input and candidate_path.is_dir() and candidate_path.exists()

        if is_valid:
            self.status_label.setText("✔ Valid Directory")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        elif not candidate_path:
            self.status_label.setText("Please select or input a directory")
            self.status_label.setStyleSheet("color: gray;")
        else:
            self.status_label.setText("✘ Invalid Directory")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    @override
    def isComplete(self) -> bool:
        if not self.custom_mods_dir_checkbox.isChecked():
            return True
        
        if not self.mods_dir_input.text().strip():
            return False

        path = Path(self.mods_dir_input.text())
        return path and path.is_dir() and path.exists()

class PreferencesPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Preferences")
        self.setSubTitle("WIP")

class SummaryPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Summary")
        self.setSubTitle("Review your settings before finishing.")
        self.summary_label: QLabel = QLabel()
        self.summary_label.setWordWrap(True)

        wizard_mhw_dir = self.field("wizard_mhw_dir")  # pyright: ignore[reportAny]

        self.summary_label.setText(
            f"<b>MHW Location:</b> {wizard_mhw_dir}</br>"
        )

class FirstTimeSetupWizard(QWizard):
    new_config_update: Signal = Signal(AppConfig)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MGR Setup Wizard")
        self.setFixedSize(700, 500)

        self._wizard_app_config: AppConfig = AppConfig()

        self.addPage(WelcomePage())
        self.addPage(MHWLocationPage())
        self.addPage(ModsLocationPage())
        self.addPage(PreferencesPage())
        self.addPage(SummaryPage())

        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.finished.connect(self._on_finished)

    @property
    def wizard_app_config(self):
        return self._wizard_app_config

    def _on_finished(self, result: QWizard.DialogCode) -> None:
        if result == QWizard.DialogCode.Accepted:
            custom_mods_dir_checkbox: bool = self.field("custom_mods_dir_checkbox")  # pyright: ignore[reportAny]

            self._wizard_app_config = AppConfig(
                mhw_dir = self.field("wizard_mhw_dir"),  # pyright: ignore[reportAny]
                mgr_mods_dir = self.field("wizard_mods_dir") if custom_mods_dir_checkbox else MGR_MODS_DIR
            )
            self.new_config_update.emit(self._wizard_app_config)

    



