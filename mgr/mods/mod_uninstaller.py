from PySide6.QtCore import QObject

class ModUninstaller(QObject):
    def __init__(self):
        super().__init__()

    def uninstall_mods(self, mod_names: list[str]):
        for mod_name in mod_names:
            