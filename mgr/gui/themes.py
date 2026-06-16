from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

PaletteColor = QColor | Qt.GlobalColor

@dataclass(frozen = True)
class Theme:
    window: PaletteColor
    window_text: PaletteColor
    base: PaletteColor
    alternate_base: PaletteColor
    text: PaletteColor
    button: PaletteColor
    button_text: PaletteColor
    highlight: PaletteColor
    highlighted_text: PaletteColor

LIGHT_THEME = Theme(
    window = QColor(240, 240, 240),
    window_text = Qt.GlobalColor.black,
    base = QColor(255, 255, 255),
    alternate_base = QColor(233, 233, 233),
    text = Qt.GlobalColor.black,
    button = QColor(240, 240, 240),
    button_text = Qt.GlobalColor.black,
    highlight = QColor(0, 120, 215),
    highlighted_text = Qt.GlobalColor.white,
)

def apply_theme(app: QApplication, theme: Theme):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, theme.window)
    palette.setColor(QPalette.ColorRole.WindowText, theme.window_text)
    palette.setColor(QPalette.ColorRole.Base, theme.base)
    palette.setColor(QPalette.ColorRole.AlternateBase, theme.alternate_base)
    palette.setColor(QPalette.ColorRole.Text, theme.text)
    palette.setColor(QPalette.ColorRole.Button, theme.button)
    palette.setColor(QPalette.ColorRole.ButtonText, theme.button_text)
    palette.setColor(QPalette.ColorRole.Highlight,theme.highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, theme.highlighted_text)
    app.setPalette(palette)