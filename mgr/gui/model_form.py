from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QLabel, QPushButton, QVBoxLayout, QWidget
)
import loguru
from pydantic import BaseModel, ValidationError
from mgr.configs.helpers.helpers import build_field_errors
from mgr.configs.services.base_config_service import ConfigService

logger = loguru.logger


class ModelForm[T: BaseModel](QDialog):
    def __init__(
        self,
        config_service: ConfigService[T],
        validation_error: ValidationError | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._service: ConfigService[T] = config_service
        self.inputs: dict[str, QLineEdit] = {}
        self.errors: dict[str, QLabel] = {}

        self._body: QVBoxLayout = QVBoxLayout(self)
        self._form: QFormLayout = QFormLayout()
        self._body.addLayout(self._form)

        if validation_error is not None:
            self._build_fields(validation_error)

        submit = QPushButton("Submit")
        submit.clicked.connect(self._on_submit)
        self._body.addWidget(submit)

    def _build_fields(self, validation_error: ValidationError) -> None:
        """Create one input + label row per errored field. Called once."""
        for field_error in build_field_errors(validation_error):
            value = field_error.field_value
            line_input = QLineEdit("" if value is None else str(value))
            error_label = QLabel()
            error_label.setStyleSheet("color: red;")

            self.inputs[field_error.field_name] = line_input
            self.errors[field_error.field_name] = error_label

            self._form.addRow(field_error.field_name, line_input)
            self._form.addRow("", error_label)

        self._show_errors(validation_error)

    def _on_submit(self) -> None:
        data = {name: w.text() for name, w in self.inputs.items() if w.text().strip()}
        try:
            self._service.update(data)
        except ValidationError as exc:
            self._show_errors(exc)
        else:
            self.accept()

    def _show_errors(self, validation_error: ValidationError) -> None:
        """Update label text only. Does not create or destroy widgets."""
        for label in self.errors.values():
            label.clear()
        for field_error in build_field_errors(validation_error):
            label = self.errors.get(field_error.field_name)
            if label is not None:
                label.setText(field_error.message)
            else:
                logger.debug(
                    f"No input row for errored field {field_error.field_name!r} " +
                    "it was not in the initial error set."
                )