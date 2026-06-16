from collections import defaultdict
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, override
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QPersistentModelIndex

from mgr.core.app_context import AppContext
from mgr.mods.mod_service import ModService
from mgr.mods.models.loaded_mod import LoadedMod


class ColumnLabels(StrEnum):
    MOD = "Mod"
    CREATOR = "Creator"
    # DISPLAY_NAME = "Display Name"  # Planned feature?
    IDS = "IDs"
    # STATUS = "Status"  # Planned feature
    # INSTALLATION = "Installation"  # Planned feature
    SIZE = "Size"
    # NOTES = "Notes"  # Planned feature


@dataclass
class TreeNode:
    """A single row in the tree.

    There are two kinds of node:

    - A *group* node sits at the top level. If several mods share the same
      name, the group shows a summary row and lists each mod as a child.
      If only one mod has that name, the group just displays that mod.
    - A *child* node represents one individual mod nested under a group.

    `row` is the node's position among its siblings. `parent` is None for
    top-level groups and points at the owning group for children.
    """
    name: str
    mods: list[LoadedMod]
    row: int
    parent: "TreeNode | None" = None
    children: list["TreeNode"] = field(default_factory=list)

    @property
    def is_expandable_group(self) -> bool:
        """True when this group holds more than one mod under a shared name."""
        return self.parent is None and len(self.mods) > 1

    @property
    def mod(self) -> LoadedMod:
        """The single mod this node represents (only valid for non-group rows)."""
        return self.mods[0]


class ModItemModel(QAbstractItemModel):
    _COLUMNS: list[ColumnLabels] = list(ColumnLabels)

    def __init__(self, app_context: AppContext):
        super().__init__()
        self._app_context: AppContext = app_context
        self._mods: ModService = self._app_context.mod_service
        self._groups: list[TreeNode] = []
        self._checked: set[LoadedMod] = set()
        self._rebuild()
        self._mods.mods_changed.connect(self._on_mods_changed)

    @property
    def checked_mods(self) -> set[LoadedMod]:
        """The mods currently ticked — hand this to batch operations like uninstall."""
        return set(self._checked)

    def _rebuild(self) -> None:
        """Group every mod by name and build the top-level rows (and any children)."""
        mods_by_name: dict[str, list[LoadedMod]] = defaultdict(list)
        for mod in self._mods.registry.all_mods:
            mods_by_name[mod.name].append(mod)

        self._groups = []
        for row, (name, mods) in enumerate(mods_by_name.items()):
            group = TreeNode(name=name, mods=mods, row=row)
            if len(mods) > 1:
                group.children = [
                    TreeNode(name=name, mods=[mod], row=child_row, parent=group)
                    for child_row, mod in enumerate(mods)
                ]
            self._groups.append(group)

        # Drop any ticked mods that no longer exist after the refresh.
        live_mods = {mod for group in self._groups for mod in group.mods}
        self._checked &= live_mods

    def _node(self, index: QModelIndex | QPersistentModelIndex) -> TreeNode:
        """Pull the TreeNode stored on an index."""
        return index.internalPointer()

    @override
    def index(self, row: int, column: int, parent: QModelIndex | QPersistentModelIndex | None = None) -> QModelIndex:
        parent = parent if parent is not None else QModelIndex()
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        # Top-level rows are the groups themselves.
        if not parent.isValid():
            return self.createIndex(row, column, self._groups[row])

        # Otherwise the row is a child of the parent group.
        parent_node = self._node(parent)
        if 0 <= row < len(parent_node.children):
            return self.createIndex(row, column, parent_node.children[row])
        return QModelIndex()

    @override
    def parent(self, index: QModelIndex | QPersistentModelIndex | None = None) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if index is None or not index.isValid():
            return QModelIndex()
        node = self._node(index)
        if node.parent is None:
            return QModelIndex()
        return self.createIndex(node.parent.row, 0, node.parent)

    @override
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        parent = parent if parent is not None else QModelIndex()
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self._groups)
        return len(self._node(parent).children)

    @override
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        return len(self._COLUMNS)

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:  # pyright: ignore[reportExplicitAny]
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._COLUMNS[section]
        return None

    def _mods_of(self, node: TreeNode) -> list[LoadedMod]:
        """The mods a node represents: its children's mods for a group, else itself.

        A checkbox on a group row stands in for all the mods beneath it, so
        toggling or reading that row works on this whole list at once.
        """
        if node.is_expandable_group:
            return [child.mod for child in node.children]
        return [node.mod]

    def _check_state(self, node: TreeNode) -> Qt.CheckState:
        """Checked only when *every* mod this node represents is ticked."""
        mods = self._mods_of(node)
        all_checked = all(mod in self._checked for mod in mods)
        return Qt.CheckState.Checked if all_checked else Qt.CheckState.Unchecked

    @override
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        base = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        # The checkbox lives in column 0 only.
        if index.column() == 0:
            base |= Qt.ItemFlag.ItemIsUserCheckable
        return base

    @override
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        node = self._node(index)

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            return self._check_state(node)

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        column = self._COLUMNS[index.column()]
        if node.is_expandable_group:
            return self._group_summary(node, column)
        if node.parent is None:
            return self._single_mod_row(node.mod, column)
        return self._child_mod_row(node.mod, column)

    @override
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:  # pyright: ignore[reportExplicitAny]
        if not index.isValid() or role != Qt.ItemDataRole.CheckStateRole or index.column() != 0:
            return False

        node = self._node(index)
        # Toggle every mod this row owns (one mod for a leaf, all children for a group).
        now_checked = Qt.CheckState(value) == Qt.CheckState.Checked
        for mod in self._mods_of(node):
            if now_checked:
                self._checked.add(mod)
            else:
                self._checked.discard(mod)

        self._emit_check_changed(index, node)
        return True

    def _emit_check_changed(self, index: QModelIndex | QPersistentModelIndex, node: TreeNode) -> None:
        """Tell the view this row changed, plus any parent/children whose box follows it."""
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

        # A leaf's change can flip its parent's "all checked?" box.
        if node.parent is not None:
            parent_index = self.parent(index)
            self.dataChanged.emit(parent_index, parent_index, [Qt.ItemDataRole.CheckStateRole])

        # A group's change cascades to every child box.
        if node.children:
            first = self.index(0, 0, index)
            last = self.index(len(node.children) - 1, 0, index)
            self.dataChanged.emit(first, last, [Qt.ItemDataRole.CheckStateRole])

    def _group_summary(self, group: TreeNode, column: ColumnLabels):
        """Summary row for a name shared by several mods."""
        match column:
            case ColumnLabels.MOD:
                return group.name
            case ColumnLabels.CREATOR:
                creators = {mod.creator for mod in group.mods}
                return next(iter(creators)) if len(creators) == 1 else "Multiple"
            case ColumnLabels.IDS:
                return f"{len(group.mods)} variants"
            case ColumnLabels.SIZE:
                return sum(mod.size for mod in group.mods)

    def _single_mod_row(self, mod: LoadedMod, column: ColumnLabels):
        """A name owned by a single mod: behaves like an ordinary row."""
        match column:
            case ColumnLabels.MOD:
                return mod.name
            case ColumnLabels.CREATOR:
                return mod.creator
            case ColumnLabels.IDS:
                return f"{mod.combined_ids}"
            case ColumnLabels.SIZE:
                return mod.size

    def _child_mod_row(self, mod: LoadedMod, column: ColumnLabels):
        """A child row identifies its mod by the combined ids."""
        match column:
            case ColumnLabels.MOD:
                return f"{mod.combined_ids}"
            case ColumnLabels.CREATOR:
                return mod.creator
            case ColumnLabels.IDS:
                return f"{mod.combined_ids}"
            case ColumnLabels.SIZE:
                return mod.size

    def _on_mods_changed(self):
        self.beginResetModel()
        self._rebuild()
        self.endResetModel()