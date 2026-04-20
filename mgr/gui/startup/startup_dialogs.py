from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QWidget

from mgr.core.app_context import AppContext

class LoadingDialog(QDialog):
    _on_text_update: Signal = Signal(str)

    def __init__(
        self,
        app_context: AppContext,
        debug: bool = False,
        title: str = "Loading...",
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedWidth(520)
        self.setFixedHeight(300)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        self._aborted: bool = False

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        text = QLineEdit()

        layout.addWidget(text)