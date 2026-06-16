"""Popup dialog that lets the user correct fields that failed pydantic validation."""
from typing import Any, NamedTuple

from pydantic import BaseModel, ValidationError
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from mgr.configs.services.config_service import ConfigService

# A "loc" is pydantic's address for a field, e.g. ("mhw_dir",) for a top-level
# field or ("nexus_ids", "0000", "creator") for a nested one.
type Loc = tuple[int | str, ...]
type JsonDict = dict[str, Any]  # pyright: ignore[reportExplicitAny]

ERROR_LABEL_STYLE = "color: #c0392b; font-size: 11px;"


class FieldRow(NamedTuple):
    """The two widgets that make up one row of the form."""
    editor: QLineEdit
    error_label: QLabel


class ValidatedInputDialog[T: BaseModel](QDialog):
    """Shows one editable row per invalid field.

    Pressing OK re-runs the model's validation. The dialog only closes when
    the input is valid, and the corrected values are then in `self.patch`.
    """

    def __init__(
        self,
        config_service: ConfigService[T],
        error: ValidationError,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service: ConfigService[T] = config_service
        self._rows: dict[Loc, FieldRow] = {}
        self.patch: JsonDict = {}

        self._set_window_title()
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Some settings are missing or invalid. Please correct them below."))

        self._form: QFormLayout = QFormLayout()
        layout.addLayout(self._form)

        # One row in the form for each validation error.
        for err in error.errors():
            loc: Loc = tuple(err["loc"])
            self._add_row(loc, err["msg"])

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------
    # Building the form
    # ------------------------------------------------------------------

    def _set_window_title(self) -> None:
        title = self._service.model.model_config.get("title")
        if title is None:
            title = self._service.model.__name__
        self.setWindowTitle(f"Fix {title}")

    def _add_row(self, loc: Loc, message: str) -> None:
        # If this field already has a row (a field can fail more than one
        # check), just add the new message to its existing error label.
        if loc in self._rows:
            label = self._rows[loc].error_label
            label.setText(label.text() + "\n" + message)
            return

        editor = QLineEdit(self)
        current_value = self._current_value(loc)
        if current_value is not None:
            editor.setText(str(current_value))

        error_label = QLabel(message, self)
        error_label.setWordWrap(True)
        error_label.setStyleSheet(ERROR_LABEL_STYLE)

        self._form.addRow(self._display_name(loc), editor)
        self._form.addRow("", error_label)

        self._rows[loc] = FieldRow(editor=editor, error_label=error_label)

    def _display_name(self, loc: Loc) -> str:
        """The label shown next to the editor.

        Uses the field's display_name from json_schema_extra if it has one,
        otherwise falls back to the dotted path, e.g. "nexus_ids.0000.creator".
        """
        fallback = ".".join(str(part) for part in loc)

        if not loc:
            return "?"

        top_level_field_name = str(loc[0])
        field_info = self._service.model.model_fields.get(top_level_field_name)
        if field_info is None:
            return fallback

        extra = field_info.json_schema_extra
        if not isinstance(extra, dict):
            return fallback

        display_name = extra.get("display_name")
        if not isinstance(display_name, str):
            return fallback

        return display_name

    def _current_value(self, loc: Loc) -> object:
        """Look up the field's current value in the merged config data,
        so the editor starts prefilled. Returns None if there is no value."""
        node: object = self._service.merged_data
        for key in loc:
            if not isinstance(node, dict):
                return None
            if key not in node:
                return None
            node = str(node[key])
        return node

    # ------------------------------------------------------------------
    # OK button: build a patch, re-validate, close only if valid
    # ------------------------------------------------------------------

    def _build_patch(self) -> JsonDict:
        """Collect the editors' text into one patch dict.

        Each value is nested under its loc: a loc of ("a", "b") with text "x"
        becomes {"a": {"b": "x"}}. Empty editors are left out of the patch
        entirely, so the model's defaults (or its "field required" error)
        apply instead of an explicit None.
        """
        patch: JsonDict = {}

        for loc, row in self._rows.items():
            text = row.editor.text().strip()
            if text == "":
                continue
            if len(loc) == 0:
                continue

            # Walk down the patch dict, creating empty dicts along the way,
            # until we reach the parent of the final key.
            node = patch
            for key in loc[:-1]:
                key_str = str(key)
                if key_str not in node:
                    node[key_str] = {}
                node = node[key_str]

            final_key = str(loc[-1])
            node[final_key] = text

        return patch

    def _on_ok(self) -> None:
        candidate = self._build_patch()
        try:
            _ = self._service.try_validate(candidate)
        except ValidationError as err:
            # Still invalid: show the new messages and keep the dialog open.
            self._show_errors(err)
            return

        self.patch = candidate
        self.accept()

    def _show_errors(self, error: ValidationError) -> None:
        # Clear all old messages first...
        for row in self._rows.values():
            row.error_label.setText("")

        # ...then fill in the fresh ones next to their fields.
        for err in error.errors():
            loc: Loc = tuple(err["loc"])
            row = self._rows.get(loc)
            if row is None:
                continue
            new_text = (row.error_label.text() + "\n" + err["msg"]).strip()
            row.error_label.setText(new_text)