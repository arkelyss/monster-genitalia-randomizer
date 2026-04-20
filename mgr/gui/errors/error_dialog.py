from PyQt6.QtWidgets import QMessageBox

CRITICAL = "critical"
WARNING = "warning"

def show_error_dialog(error: Exception, severity: str, title: str):
    msg = QMessageBox()

    if severity == CRITICAL:
        msg.setIcon(QMessageBox.Icon.Critical)
    elif severity == WARNING:
        msg.setIcon(QMessageBox.Icon.Warning)

    msg.setText(str(error))
    msg.setWindowTitle(title)

    if error.__cause__:
        cause_message = f"Original error: {error.__cause__}"
        msg.setDetailedText(cause_message)

    msg.exec()