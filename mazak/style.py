APP_STYLESHEET = """
QMainWindow {
    background-color: #eef0f3;
}

QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #dde1e6;
    padding: 8px;
    spacing: 4px;
}

QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    padding: 6px 12px;
    color: #3c4043;
    font-size: 12px;
}

QToolBar QToolButton:hover {
    background-color: #f1f3f6;
    border: 1px solid #e2e5ea;
}

QToolBar QToolButton:pressed {
    background-color: #e4e9f5;
}

QToolBar QToolButton:checked {
    background-color: #e5edff;
    border: 1px solid #2f6fed;
    color: #1a4fc4;
}

QToolBar::separator {
    background-color: #e1e4e9;
    width: 1px;
    margin: 6px 6px;
}

QGraphicsView {
    background-color: #cfd4da;
    border: none;
}

QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #dde1e6;
    color: #5f6368;
}

QFrame#propertiesPanel {
    background-color: #ffffff;
    border: 1px solid #e3e6ea;
    border-radius: 14px;
}

QFrame#propertiesPanel QLabel#sectionLabel {
    color: #9aa0a6;
    font-size: 10px;
    font-weight: 600;
}

QFrame#propertiesPanel QFrame#panelSeparator {
    background-color: #e6e9ed;
    max-width: 1px;
    min-width: 1px;
}

QFrame#propertiesPanel QFrame#panelHSeparator {
    background-color: #e6e9ed;
    max-height: 1px;
    min-height: 1px;
    border: none;
}

QFrame#propertiesPanel QLineEdit {
    border: 1px solid #dde1e6;
    border-radius: 8px;
    padding: 5px 10px;
    background-color: #f8f9fb;
}

QFrame#propertiesPanel QLineEdit:focus {
    border: 1px solid #2f6fed;
    background-color: #ffffff;
}

QFrame#propertiesPanel QFontComboBox,
QFrame#propertiesPanel QSpinBox {
    border: 1px solid #dde1e6;
    border-radius: 8px;
    padding: 3px 6px;
    background-color: #f8f9fb;
}

QFrame#propertiesPanel QToolButton {
    background-color: transparent;
    border: 2px solid transparent;
    border-radius: 8px;
    padding: 2px;
}

QFrame#propertiesPanel QToolButton:hover {
    background-color: #f1f3f6;
}

QFrame#propertiesPanel QToolButton:checked {
    background-color: #eef1f6;
    border: 2px solid #2f6fed;
}

QFrame#propertiesPanel QToolButton[swatch="true"] {
    border-radius: 17px;
}
"""
