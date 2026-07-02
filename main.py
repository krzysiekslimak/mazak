import os
import sys

os.environ.setdefault("QT_SCALE_FACTOR", "1.15")

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from mazak.main_window import MainWindow


def _force_light_palette(app: QApplication):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#eef0f3"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f8f9fb"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#9aa0a6"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2f6fed"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mazak")
    _force_light_palette(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
