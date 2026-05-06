from pathlib import Path
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QPixmap
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget, QMainWindow

from mgr.core.app_context import AppContext
from mgr.core.constants import FONT_FIRLEST_REGULAR, IMAGES_DIR, APP_VERSION, PALICO_PNG
from mgr.gui.mod_table import ModTable

class MainWindow(QMainWindow):
    def __init__(self, app: AppContext):
        super().__init__()
        self.app: AppContext = app
        self.setWindowTitle(f"Monster Genitalia Randomizer v{APP_VERSION}")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background-color: #2d2d2f;")
        self.setAcceptDrops(True)

        # Add the firlest font for the MGR text logo
        font_firlest_id: int = QFontDatabase.addApplicationFont(str(FONT_FIRLEST_REGULAR))
        font_firlest_families: list[str] = QFontDatabase.applicationFontFamilies(font_firlest_id)
        self._font_firlest_family: str = font_firlest_families[0]

        self._navbar_button_names: list[str] = ["Home", "Mod Library", "Settings", "Credits"]
        self.stack: QStackedWidget = QStackedWidget()

        self._build_ui()

    def _build_ui(self) -> None:
        base_container: QWidget = QWidget()
        base_layout = QHBoxLayout(base_container)
        base_layout.setContentsMargins(0,0,0,0)
        base_layout.setSpacing(0)

        base_layout.addWidget(self._build_navbar())
        base_layout.addWidget(self._build_body())

        self.setCentralWidget(base_container)

    def _build_navbar(self):
        navbar = QWidget()
        navbar.setFixedWidth(250)
        navbar.setStyleSheet("background-color: #323639;")
        navbar_layout = QVBoxLayout(navbar)
        navbar_layout.setContentsMargins(0,0,0,0)

        image = QPixmap(PALICO_PNG)
        image_label = QLabel()
        image_label.setContentsMargins(0,0,0,0)
        image_label.setPixmap(image.scaled(230, 230))

        text_group = QWidget()
        text_group_layout = QHBoxLayout(text_group)
        text_group.setFixedHeight(130)
        text_group_layout.setSpacing(0)

        text_label = QLabel("MGR")
        text_label.setFont(QFont(self._font_firlest_family, 48))

        subtext_label = QLabel(f"v{APP_VERSION}")
        subtext_label.setFont(QFont("Source Pro", 10))
        subtext_label.setContentsMargins(2,50,0,0)


        text_group_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)
        text_group_layout.addWidget(subtext_label, alignment=Qt.AlignmentFlag.AlignCenter)

        navbar_layout.addWidget(text_group, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        # navbar_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        navbar_layout.addWidget(self._build_navbar_buttons(), alignment=Qt.AlignmentFlag.AlignTop)

        navbar_layout.addStretch(1)

        navbar_layout.addWidget(self._build_navbar_footer(), alignment=Qt.AlignmentFlag.AlignBottom)

        return navbar

    def _build_navbar_buttons(self) -> QWidget:
        button_box = QWidget()
        button_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button_box_layout = QVBoxLayout(button_box)
        button_box_layout.setContentsMargins(0,0,0,0)
        button_box_layout.setSpacing(0)

        # Make a button group and set exclusive so that buttons automatically toggle checked states.
        nav_group: QButtonGroup = QButtonGroup(self)
        nav_group.setExclusive(True)
        

        def _make_button(button_name: str, stack_index_assignment: int, icon_file: Path | None = None) -> QPushButton:
            # Factory for applying bulk settings to buttons.
            # Stack_index_assignment connects buttons with respective stack indexes.
            button = QPushButton(button_name)
            if icon_file is not None:
                button.setIcon(QIcon(str(icon_file)))
                button.setIconSize(QSize(30,30))
            button.setFixedHeight(50)
            button.setFont(QFont("Roboto", 14))
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding-left: 15px;
                    border-left: 5px solid transparent;
                    text-align: left;
                    color: #DBDBDB;
                }
                QPushButton:hover {
                    background-color: #3d4145;
                }
                QPushButton:pressed {
                    background-color: #3d4145;
                }
                QPushButton:checked {
                    border-left: 5px solid orange;
                }
            """)
            button.clicked.connect(lambda: self.stack.setCurrentIndex(stack_index_assignment))
            nav_group.addButton(button)
            return button

        # Make the home button separately so it can be set as the default
        home_button = _make_button("     Home", 0, IMAGES_DIR / "home_icon.png")

        button_box_layout.addWidget(home_button)
        button_box_layout.addWidget(_make_button("     Mod Library", 1, IMAGES_DIR / "mod_library_icon.png"))
        button_box_layout.addWidget(_make_button("     Settings", 2, IMAGES_DIR / "settings_icon.png"))
        button_box_layout.addWidget(_make_button("     Credits", 3, IMAGES_DIR / "credits_icon.png"))

        # Set home button as default and set the stack's current index to 0 to synchronize
        home_button.setChecked(True)
        self.stack.setCurrentIndex(0)

        return button_box

    def _build_body(self) -> QWidget:
        body = QWidget()
        body_layout = QVBoxLayout(body)

        body_layout.addWidget(self.stack)

        self.stack.addWidget(HomePage())
        self.stack.addWidget(ModsLibraryPage())
        self.stack.addWidget(SettingsPage())
        self.stack.addWidget(CreditsPage())

        return body

    def _build_navbar_footer(self):
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)

        help_button = QPushButton("(?) Help")

        footer_layout.addWidget(help_button)

        return footer

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        mod_page_layout = QVBoxLayout(self)

        mod_page_layout.addWidget(self._build_header())
        mod_page_layout.addWidget(self._build_body())
        mod_page_layout.addStretch(1)
        mod_page_layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget(self)
        header.setFixedHeight(100)
        # header.setStyleSheet("background-color: gray;")
        _ = QHBoxLayout(header)
        return header

    def _build_body(self):
        body = QWidget()
        # body.setStyleSheet("background-color: gray;")
        body_layout = QVBoxLayout(body)

        greeting_text = QLabel(
            "Hello!\n\n"+
            f"You've landed on build {APP_VERSION} of MGR. We are currently in the very early stages of alpha development, so expect everything"+
            "to break (features, functionality, design, updates etc).\n\n"+
            "If you're here to participate in testing or contribute to the project, then welcome aboard! I'll take all the help I can get. "+
            "For a full list of ways you can help, check out the README.md in the links below.\n\n"+
            "Good luck, and happy hunting!\n\n"+
            "   - Arkelyss\n\n"
        )
        greeting_text.setWordWrap(True)
        greeting_text.setFont(QFont("Georgia", 12))
        greeting_text.setStyleSheet("color: #BFBFBF;")

        link_text = QLabel(
            "GitHub Project (and README): <a href='https://github.com/arkelyss/monster-genitalia-randomizer/tree/develop'>https://github.com/arkelyss/monster-genitalia-randomizer/tree/develop</a>"
        )
        link_text.setFont(QFont("Georgia", 12))
        link_text.setOpenExternalLinks(True)
        link_text.setStyleSheet("color: #BFBFBF;")

        body_layout.addWidget(greeting_text, Qt.AlignmentFlag.AlignTop)
        body_layout.addWidget(link_text)

        return body

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        _ = QHBoxLayout(footer)
        return footer


class ModsLibraryPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        mod_page_layout = QVBoxLayout(self)

        mod_page_layout.addWidget(self._build_header())
        mod_page_layout.addWidget(self._build_body())
        mod_page_layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget(self)
        _ = QHBoxLayout(header)
        return header

    def _build_body(self):
        body = QWidget()
        body_layout = QVBoxLayout(body)

        body_layout.addWidget(ModTable(body))
        return body

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)

        button_box = QWidget()
        button_box.setFixedSize(150,150)
        button_box_layout = QVBoxLayout(button_box)

        big_button_box = QWidget()
        big_button_box.setFixedSize(200, 100)
        big_button_box_layout = QHBoxLayout(big_button_box)

        option_box = QWidget()
        _ = QHBoxLayout(option_box)

        install_button = QPushButton("Install")
        uninstall_button = QPushButton("Uninstall")
        deploy_button = QPushButton("Deploy")
        deploy_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        install_button.setDisabled(True)
        uninstall_button.setDisabled(True)

        footer_layout.addWidget(option_box)
        footer_layout.addWidget(button_box)
        footer_layout.addWidget(big_button_box)
        button_box_layout.addWidget(install_button)
        button_box_layout.addWidget(uninstall_button)
        big_button_box_layout.addWidget(deploy_button)

        return footer

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        settings_layout = QVBoxLayout(self)
        settings_layout.addWidget(self._build_header())
        settings_layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        header = QWidget()
        _ = QHBoxLayout(header)
        return header

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        _ = QHBoxLayout(footer)
        return footer

class CreditsPage(QWidget):
    def __init__(self):
        super().__init__()
        # self._build_ui()