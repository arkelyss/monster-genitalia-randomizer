# pyright: reportIncompatibleMethodOverride=false

from functools import partial
from pathlib import Path
from typing import override

from PySide6.QtCore import QAbstractItemModel, QPoint, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMenu, QTreeView, QWidget

from mgr.core.constants import APP_CHECKMARK_IMAGE
from mgr.mods.models.enums import SupportedArchiveTypes

# Columns at this index or below are shown by default; anything higher starts hidden.
LAST_VISIBLE_COLUMN = 4
# Default width for the first (name) column.
NAME_COLUMN_WIDTH = 800


class PersistentMenu(QMenu):
    '''Keep column-toggle context menus open when a checkable action is clicked.'''

    @override
    def mouseReleaseEvent(self, event: QMouseEvent):
        action = self.activeAction()
        if action and action.isCheckable():
            action.trigger()
            return
        super().mouseReleaseEvent(event)


class ModTreeView(QTreeView):
    mod_archives_dropped: Signal = Signal(list)

    def __init__(self, model: QAbstractItemModel, parent: QWidget | None = None):
        super().__init__(parent)
        self._model: QAbstractItemModel = model
        self.setModel(model)
        self.setAcceptDrops(True)

        self._configure_view()
        self._configure_header()

    def _configure_view(self):
        # NoEditTriggers blocks text editors, NOT checkbox clicks
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # No text editing (for example, double clicks). May change later.
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # Select whole rows
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)  # Allow multi-select
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Not reachable via Tab
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)  # Show expand arrows for shared-name groups
        self.setUniformRowHeights(True)
        self.setContentsMargins(0, 0, 0, 0)

        # Place a border around the checkboxes and use a checkmark image when checked
        self.setStyleSheet(f"""
            QTreeView::indicator {{
                width: 14px;
                height: 14px;
                border: 2px solid #555555; /* Your custom border color/thickness */
                border-radius: 3px;        /* Optional: rounded corners */
                background-color: #ffffff;
            }}

            QTreeView::indicator:checked {{
                image: url({APP_CHECKMARK_IMAGE});
                padding: 2px;
            }}
        """)

    def _configure_header(self):
        header = self.header()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._show_header_context_menu)
        header.resizeSection(0, NAME_COLUMN_WIDTH)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)

        for column in range(header.count()):
            if column <= LAST_VISIBLE_COLUMN:
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)
            else:
                self._toggle_column(column, visible=False)

    def _toggle_column(self, column: int, visible: bool):
        self.setColumnHidden(column, not visible)

    def _has_only_valid_archives(self, event: QDropEvent | QDragEnterEvent) -> bool:
        '''True if archive payload contains only valid archives.'''
        mime = event.mimeData()
        if not (mime and mime.hasUrls()):
            return False
        valid_suffixes = tuple(SupportedArchiveTypes)
        return all(
            url.toLocalFile().lower().endswith(valid_suffixes)
            for url in mime.urls()
        )

    @override
    def dragEnterEvent(self, event: QDragEnterEvent):
        self._accept_or_ignore(event)

    # Continuously analyzes payload as cursor movement occurs
    @override
    def dragMoveEvent(self, event: QDragEnterEvent):
        self._accept_or_ignore(event)

    def _accept_or_ignore(self, event: QDragEnterEvent):
        if self._has_only_valid_archives(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    @override
    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()
        if mime and mime.hasUrls():
            paths = [Path(url.toLocalFile()) for url in mime.urls()]
            self.mod_archives_dropped.emit(paths)

    def _show_header_context_menu(self, pos: QPoint):
        header = self.header()
        menu = PersistentMenu(self)

        # Column 0 (name) stays visible, so the menu starts at column 1.
        for column in range(1, header.count()):
            label = self._model.headerData(
                column, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            ) or f"Column {column + 1}"

            action = menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(not header.isSectionHidden(column))
            action.toggled.connect(partial(self._toggle_column, column))

        menu.exec(header.mapToGlobal(pos))