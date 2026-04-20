# pyright: reportExplicitAny=false
# pyright: reportAny=false

from typing import Any, override
from PyQt6.QtWidgets import QComboBox
from PySide6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QWidget
from PySide6.QtCore import QAbstractItemModel, QModelRoleData
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QPersistentModelIndex, Signal, Slot
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QObject, QTimer, Qt
from PySide6.QtGui import QBrush, QFont, QColor

class MyModel(QAbstractTableModel):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._people: list[list[str | int | str]] = [
            ["Alice", 30, "Engineer"],
            ["Bob", 25, "Designer"],
            ["Carol", 35, "Manager"],
        ]

    @override
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        return len(self._people)

    @override
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        return max([len(i) for i in self._people])

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ["Name", "Age", "Role"][section]
        if role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font

    @override
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        
        cell_value = self._people[index.row()][index.column()]

        if role == Qt.ItemDataRole.BackgroundRole and cell_value == "Engineer":
            return QBrush(QColor("lightgreen"))

        if role == Qt.ItemDataRole.DisplayRole:
            return cell_value

        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() == 1:
            return Qt.AlignmentFlag.AlignRight

    @override
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Any:
        if index.column() == 1:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    @override
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = Qt.ItemDataRole.DisplayRole) -> bool:
        if not index.isValid():
            return False
        
        if role == Qt.ItemDataRole.EditRole:
            self._people[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        
        return False

    def add_person(self, row_data: list[str | int | str]):
        insert_at = len(self._people)
        self.beginInsertRows(QModelIndex(), insert_at, insert_at)
        self._people.append(row_data)
        self.endInsertRows()

    def remove_last(self):
        last_row = len(self._people) - 1
        self.beginRemoveRows(QModelIndex(), last_row, last_row)
        self._people.pop(last_row)
        self.endRemoveRows()

class RoleDelegate(QStyledItemDelegate):
    @override
    def createEditor(self, parent: QWidget | None, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        pass
    
    @override
    def setEditorData(self, editor: QWidget | None, index: QModelIndex | QPersistentModelIndex) -> None:
        pass

    @override
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None:
        pass

class AgeDelegate(QStyledItemDelegate):
    @override
    def createEditor(self, parent: QWidget | None, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QWidget:
        combo_box = QComboBox()
        return combo_box
    
    @override
    def setEditorData(self, editor: QWidget | None, index: QModelIndex | QPersistentModelIndex) -> None:
        if not index.isValid():
            return None
    

    @override
    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex | QPersistentModelIndex) -> None:
        pass

    
        


    


    