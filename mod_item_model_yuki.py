from PySide6.QtCore import QAbstractItemModel, QObject


class TreeItem:
    def __init__(self, data: list[str], parent=None):
        self.item_data: list[str] = data
        self.parent_item = parent
        self.child_items: list[str] = []

    def appendChild(self, child):
        self.child_items.append(child)

    def child(self, row):
        if 0 <= row < len(self.child_items):
            return self.child_items[row]
        return None

    def childCount(self):
        return len(self.child_items)

    def columnCount(self):
        return len(self.item_data)

    def data(self, column):
        if 0 <= column < len(self.item_data):
            return self.item_data[column]
        return None

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def parent(self):
        return self.parent_item


class TreeModel(QAbstractItemModel):
    def __init__(self, data: list[str], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.root_item = TreeItem(['Name', 'Description'])
        self._setup_model_data(data, self.root_item)
    
    def _setup_model_data(self, data: tuple[str, str, str], parent_item: TreeItem):
        for name, description, children in data: