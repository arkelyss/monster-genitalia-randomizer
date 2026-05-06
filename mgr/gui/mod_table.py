# pyright: reportIncompatibleMethodOverride=false

from typing import final, override
from PySide6.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from pathlib import Path

from mgr.core.constants import SUPPORTED_ARCHIVE_TYPES

@final
class ModTable(QTableWidget):
    mod_already_added = Signal(list)

    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self._mod_queue = []

        horizontal_header = self.horizontalHeader()
        vertical_header = self.verticalHeader()

        header_categories = ["Mod", "Target", "Status", "Size"]
        self.setColumnCount(len(header_categories))
        self.setHorizontalHeaderLabels(header_categories)

        if horizontal_header:
            horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            horizontal_header.setFixedHeight(30)
            horizontal_header.setStyleSheet("""
                QHeaderView::section {
                    background-color: #252525;
                    color: #cccccc;
                    border: none;
                    border-right: 1px solid #444444;
                    border-bottom: 1px solid #444444;
                }
            """)

        if vertical_header:
            vertical_header.hide()
            vertical_header.setDefaultSectionSize(40)

        self.setAcceptDrops(True)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setFixedHeight(500)
        self.setShowGrid(True)
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #444444;
                padding-right: -1px;
                background-color: #1e1e1e;
                alternate-background-color: #222222;
                gridline-color: #444444;
            }
            QTableWidget::item {
                padding-left: 6px;
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #2a2a4a;
                color: #ffffff;
            }
        """)
        
    @property
    def mod_queue(self) -> list[Path]:
        return self._mod_queue

    @mod_queue.setter
    def mod_queue(self, new_queue: list[Path]):
        self._mod_queue = new_queue

    def _event_contains_valid_urls(self, event: QDropEvent | QDragEnterEvent):
        mime = event.mimeData()
        if mime and mime.hasUrls():
            urls = mime.urls()
            return all(url.toLocalFile().lower().endswith(tuple(SUPPORTED_ARCHIVE_TYPES)) for url in urls)

    @override
    def dragEnterEvent(self, event: QDragEnterEvent):
        if self._event_contains_valid_urls(event):
            event.acceptProposedAction()
            return
        event.ignore()

    @override
    def dragMoveEvent(self, event: QDragEnterEvent):
        if self._event_contains_valid_urls(event):
            event.acceptProposedAction()
            return
        event.ignore()

    @override
    def dropEvent(self, event: QDropEvent):
        mime = event.mimeData()

        if mime and mime.hasUrls():
            dropped_archives = [Path(url.toLocalFile()) for url in mime.urls()]
            already_added: list[str] = []

            for path in dropped_archives:
                mod_name = path.name       

                if mod_name in [mod_path.name for mod_path in self.mod_queue]:
                    already_added.append(mod_name)
                    continue

                row = self.rowCount()
                self.setRowCount(row + 1)
                self.setItem(row, 0, QTableWidgetItem(str(mod_name)))
                self.mod_queue.append(path)

            if already_added:
                self.mod_already_added.emit(already_added)
        

    