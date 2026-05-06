from PySide6.QtWidgets import QInputDialog, QWidget

class PopupInput(QInputDialog):

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)

    def show_popup(self, title: str, text: str) -> str | None:
        msg = QInputDialog()
        msg.setWindowTitle(title)
        msg.setLabelText(text)
        msg.setOkButtonText("Ok")
        msg.setCancelButtonText("Cancel")

        if msg.exec() == QInputDialog.DialogCode.Accepted:
            return msg.textValue()
        else:
            return None