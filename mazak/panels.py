from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QColorDialog,
    QFontComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
)

from . import icons
from .i18n import tr, translator
from .tools import ArrowStyle, BubbleShape, StickerKind

ARROW_PALETTE = [
    QColor("#1e1e1e"),
    QColor("#e53935"),
    QColor("#fb8c00"),
    QColor("#43a047"),
    QColor("#1e88e5"),
    QColor("#8e24aa"),
]

BUBBLE_PALETTE = [
    QColor("#ffffff"),
    QColor("#1e1e1e"),
    QColor("#e53935"),
    QColor("#fb8c00"),
    QColor("#43a047"),
    QColor("#1e88e5"),
]

THICKNESS_OPTIONS = [("thickness_thin", 2.5), ("thickness_medium", 4.0), ("thickness_thick", 7.0)]

ARROW_STYLE_OPTIONS = [
    ("arrow_style_classic", ArrowStyle.CLASSIC),
    ("arrow_style_slim", ArrowStyle.SLIM),
    ("arrow_style_bold", ArrowStyle.BOLD),
]

BUBBLE_SHAPE_OPTIONS = [
    ("bubble_shape_rounded", BubbleShape.ROUNDED),
    ("bubble_shape_oval", BubbleShape.OVAL),
    ("bubble_shape_cloud", BubbleShape.CLOUD),
]

TEXT_PALETTE = [
    QColor("#1e1e1e"),
    QColor("#ffffff"),
    QColor("#e53935"),
    QColor("#fb8c00"),
    QColor("#43a047"),
    QColor("#1e88e5"),
]

FRAME_PALETTE = [
    QColor("#e53935"),
    QColor("#1e1e1e"),
    QColor("#fb8c00"),
    QColor("#43a047"),
    QColor("#1e88e5"),
    QColor("#8e24aa"),
]

CORNER_OPTIONS = [("corner_sharp", False), ("corner_rounded", True)]

STICKER_PALETTE = [
    QColor("#e53935"),
    QColor("#fb8c00"),
    QColor("#43a047"),
    QColor("#1e88e5"),
    QColor("#8e24aa"),
    QColor("#1e1e1e"),
]

STICKER_OPTIONS = [
    ("sticker_exclamation", StickerKind.EXCLAMATION),
    ("sticker_question", StickerKind.QUESTION),
    ("sticker_check", StickerKind.CHECK),
    ("sticker_cross", StickerKind.CROSS),
    ("sticker_star", StickerKind.STAR),
    ("sticker_warning", StickerKind.WARNING),
]

TEXT_COLOR_OPTIONS = [(QColor("#1e1e1e"), "black_text"), (QColor("#ffffff"), "white_text")]


class _IslandPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("propertiesPanel")
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(24)
        effect.setOffset(0, 4)
        effect.setColor(QColor(0, 0, 0, 55))
        self.setGraphicsEffect(effect)
        self._retranslations = []
        translator.language_changed.connect(self._retranslate)

    def _retranslate(self, _lang=None):
        for fn in self._retranslations:
            fn()

    def _section_label(self, key: str) -> QLabel:
        label = QLabel(tr(key))
        label.setObjectName("sectionLabel")
        self._retranslations.append(lambda l=label, k=key: l.setText(tr(k)))
        return label

    def _tooltip(self, widget, key: str):
        widget.setToolTip(tr(key))
        self._retranslations.append(lambda w=widget, k=key: w.setToolTip(tr(k)))

    def _button_text(self, widget, key: str):
        widget.setText(tr(key))
        self._retranslations.append(lambda w=widget, k=key: w.setText(tr(k)))

    def _vseparator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setObjectName("panelSeparator")
        return line

    def _select_color(self, buttons: dict, custom_btn: QToolButton, color: QColor):
        btn = buttons.get(color.name())
        if btn is not None:
            btn.setChecked(True)
        else:
            custom_btn.setIcon(icons.circle_swatch_icon(color))
            custom_btn.setChecked(True)

    def _color_row(self, palette, default_color, on_pick):
        row = QHBoxLayout()
        row.setSpacing(6)
        group = QButtonGroup(self)
        group.setExclusive(True)
        buttons = {}
        for color in palette:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setProperty("swatch", "true")
            btn.setFixedSize(34, 34)
            btn.setIcon(icons.circle_swatch_icon(color))
            btn.setIconSize(QSize(22, 22))
            btn.setToolTip(color.name())
            btn.clicked.connect(lambda _checked, c=color: on_pick(c))
            group.addButton(btn)
            row.addWidget(btn)
            buttons[color.name()] = btn

        custom_btn = QToolButton()
        custom_btn.setCheckable(True)
        custom_btn.setProperty("swatch", "true")
        custom_btn.setFixedSize(34, 34)
        custom_btn.setIcon(icons.custom_color_icon())
        custom_btn.setIconSize(QSize(22, 22))
        self._tooltip(custom_btn, "custom_color")
        group.addButton(custom_btn)
        row.addWidget(custom_btn)

        buttons[default_color.name()].setChecked(True)
        return row, group, buttons, custom_btn


class ArrowPropertiesPanel(_IslandPanel):
    color_changed = Signal(QColor)
    thickness_changed = Signal(float)
    shadow_toggled = Signal(bool)
    style_changed = Signal(ArrowStyle)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(18)

        outer.addLayout(self._build_color_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_thickness_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_style_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_shadow_section())
        outer.addStretch(1)

    def _build_color_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("color"))
        row, self.color_group, self._color_buttons, self.custom_color_btn = self._color_row(
            ARROW_PALETTE, ARROW_PALETTE[1], self.color_changed.emit
        )
        self.custom_color_btn.clicked.connect(self._pick_custom_color)
        col.addLayout(row)
        return col

    def _build_thickness_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("thickness"))
        row = QHBoxLayout()
        row.setSpacing(6)

        self.thickness_group = QButtonGroup(self)
        self.thickness_group.setExclusive(True)
        self._thickness_buttons = {}
        for key, value in THICKNESS_OPTIONS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setFixedSize(38, 34)
            btn.setIcon(icons.thickness_icon(value + 1))
            btn.setIconSize(QSize(26, 20))
            self._tooltip(btn, key)
            btn.clicked.connect(lambda _checked, v=value: self.thickness_changed.emit(v))
            self.thickness_group.addButton(btn)
            row.addWidget(btn)
            self._thickness_buttons[value] = btn
            if key == "thickness_medium":
                btn.setChecked(True)

        col.addLayout(row)
        return col

    def _build_style_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("shape"))
        row = QHBoxLayout()
        row.setSpacing(6)

        self.style_group = QButtonGroup(self)
        self.style_group.setExclusive(True)
        self._style_buttons = {}
        for key, style in ARROW_STYLE_OPTIONS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setFixedSize(38, 34)
            btn.setIcon(icons.arrow_style_icon(style))
            btn.setIconSize(QSize(26, 26))
            self._tooltip(btn, key)
            btn.clicked.connect(lambda _checked, s=style: self.style_changed.emit(s))
            self.style_group.addButton(btn)
            row.addWidget(btn)
            self._style_buttons[style] = btn
            if style == ArrowStyle.CLASSIC:
                btn.setChecked(True)

        col.addLayout(row)
        return col

    def _build_shadow_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("shadow"))
        self.shadow_btn = QToolButton()
        self.shadow_btn.setCheckable(True)
        self.shadow_btn.setFixedSize(38, 34)
        self.shadow_btn.setIcon(icons.shadow_icon())
        self.shadow_btn.setIconSize(QSize(24, 24))
        self._tooltip(self.shadow_btn, "shadow_tooltip_arrow")
        self.shadow_btn.toggled.connect(self.shadow_toggled.emit)
        col.addWidget(self.shadow_btn)
        return col

    def sync_from(self, color: QColor, width: float, style: ArrowStyle, shadow: bool):
        self._select_color(self._color_buttons, self.custom_color_btn, color)
        btn = self._thickness_buttons.get(width)
        if btn is not None:
            btn.setChecked(True)
        style_btn = self._style_buttons.get(style)
        if style_btn is not None:
            style_btn.setChecked(True)
        self.shadow_btn.blockSignals(True)
        self.shadow_btn.setChecked(shadow)
        self.shadow_btn.blockSignals(False)

    def _pick_custom_color(self):
        color = QColorDialog.getColor(QColor("#e53935"), self, tr("custom_color_arrow"))
        if color.isValid():
            self.custom_color_btn.setIcon(icons.circle_swatch_icon(color))
            self.custom_color_btn.setChecked(True)
            self.color_changed.emit(color)
        else:
            checked = self.color_group.checkedButton()
            if checked is None:
                self._color_buttons[ARROW_PALETTE[1].name()].setChecked(True)


class BubblePropertiesPanel(_IslandPanel):
    color_changed = Signal(QColor)
    shape_changed = Signal(BubbleShape)
    border_toggled = Signal(bool)
    shadow_toggled = Signal(bool)
    text_changed = Signal(str)
    font_changed = Signal(str)
    bold_toggled = Signal(bool)
    size_changed = Signal(int)
    text_shadow_toggled = Signal(bool)
    text_color_changed = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(18)
        top_row.addLayout(self._build_color_section())
        top_row.addWidget(self._vseparator())
        top_row.addLayout(self._build_shape_section())
        top_row.addWidget(self._vseparator())
        top_row.addLayout(self._build_border_section())
        top_row.addWidget(self._vseparator())
        top_row.addLayout(self._build_shadow_section())
        top_row.addStretch(1)
        outer.addLayout(top_row)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("panelHSeparator")
        outer.addWidget(separator)

        outer.addLayout(self._build_text_section())

    def _build_color_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("color"))
        row, self.color_group, self._color_buttons, self.custom_color_btn = self._color_row(
            BUBBLE_PALETTE, BUBBLE_PALETTE[0], self.color_changed.emit
        )
        self.custom_color_btn.clicked.connect(self._pick_custom_color)
        col.addLayout(row)
        return col

    def _build_shape_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("shape"))
        row = QHBoxLayout()
        row.setSpacing(6)

        self.shape_group = QButtonGroup(self)
        self.shape_group.setExclusive(True)
        self._shape_buttons = {}
        for key, shape in BUBBLE_SHAPE_OPTIONS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setFixedSize(38, 34)
            btn.setIcon(icons.bubble_shape_icon(shape))
            btn.setIconSize(QSize(26, 24))
            self._tooltip(btn, key)
            btn.clicked.connect(lambda _checked, s=shape: self.shape_changed.emit(s))
            self.shape_group.addButton(btn)
            row.addWidget(btn)
            self._shape_buttons[shape] = btn
            if shape == BubbleShape.ROUNDED:
                btn.setChecked(True)

        col.addLayout(row)
        return col

    def _build_border_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("border"))
        self.border_btn = QToolButton()
        self.border_btn.setCheckable(True)
        self.border_btn.setChecked(False)
        self.border_btn.setFixedSize(38, 34)
        self.border_btn.setIcon(icons.border_icon())
        self.border_btn.setIconSize(QSize(22, 22))
        self._tooltip(self.border_btn, "bubble_border_tooltip")
        self.border_btn.toggled.connect(self.border_toggled.emit)
        col.addWidget(self.border_btn)
        return col

    def _build_shadow_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("shadow"))
        self.shadow_btn = QToolButton()
        self.shadow_btn.setCheckable(True)
        self.shadow_btn.setFixedSize(38, 34)
        self.shadow_btn.setIcon(icons.shadow_icon())
        self.shadow_btn.setIconSize(QSize(24, 24))
        self._tooltip(self.shadow_btn, "shadow_tooltip_bubble")
        self.shadow_btn.toggled.connect(self.shadow_toggled.emit)
        col.addWidget(self.shadow_btn)
        return col

    def _build_text_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("text"))
        row = QHBoxLayout()
        row.setSpacing(8)

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText(tr("bubble_text_placeholder"))
        self._retranslations.append(lambda: self.text_edit.setPlaceholderText(tr("bubble_text_placeholder")))
        self.text_edit.setText(tr("default_bubble_text"))
        self.text_edit.setMinimumWidth(180)
        self.text_edit.textChanged.connect(self.text_changed.emit)
        row.addWidget(self.text_edit, 1)

        self.font_combo = QFontComboBox()
        self.font_combo.setFixedWidth(150)
        self.font_combo.currentFontChanged.connect(lambda f: self.font_changed.emit(f.family()))
        row.addWidget(self.font_combo)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(16)
        self.size_spin.setSuffix(" px")
        self.size_spin.setFixedWidth(70)
        self.size_spin.valueChanged.connect(self.size_changed.emit)
        row.addWidget(self.size_spin)

        self.bold_btn = QToolButton()
        self.bold_btn.setCheckable(True)
        self.bold_btn.setChecked(True)
        self.bold_btn.setFixedSize(34, 34)
        self.bold_btn.setIcon(icons.bold_icon())
        self.bold_btn.setIconSize(QSize(20, 20))
        self._tooltip(self.bold_btn, "bold")
        self.bold_btn.toggled.connect(self.bold_toggled.emit)
        row.addWidget(self.bold_btn)

        self.text_shadow_btn = QToolButton()
        self.text_shadow_btn.setCheckable(True)
        self.text_shadow_btn.setFixedSize(34, 34)
        self.text_shadow_btn.setIcon(icons.text_shadow_icon())
        self.text_shadow_btn.setIconSize(QSize(20, 20))
        self._tooltip(self.text_shadow_btn, "text_shadow_tooltip")
        self.text_shadow_btn.toggled.connect(self.text_shadow_toggled.emit)
        row.addWidget(self.text_shadow_btn)

        self.text_color_group = QButtonGroup(self)
        self.text_color_group.setExclusive(True)
        self._text_color_buttons = {}
        for color, key in TEXT_COLOR_OPTIONS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setProperty("swatch", "true")
            btn.setFixedSize(34, 34)
            btn.setIcon(icons.circle_swatch_icon(color))
            btn.setIconSize(QSize(22, 22))
            self._tooltip(btn, key)
            btn.clicked.connect(lambda _checked, c=color: self.text_color_changed.emit(c))
            self.text_color_group.addButton(btn)
            row.addWidget(btn)
            self._text_color_buttons[color.name()] = btn
            if color == QColor("#1e1e1e"):
                btn.setChecked(True)

        col.addLayout(row)
        return col

    def _pick_custom_color(self):
        color = QColorDialog.getColor(QColor("#ffffff"), self, tr("custom_color_bubble"))
        if color.isValid():
            self.custom_color_btn.setIcon(icons.circle_swatch_icon(color))
            self.custom_color_btn.setChecked(True)
            self.color_changed.emit(color)
        else:
            checked = self.color_group.checkedButton()
            if checked is None:
                self._color_buttons[BUBBLE_PALETTE[0].name()].setChecked(True)

    def sync_from(
        self,
        fill_color: QColor,
        shape: BubbleShape,
        border: bool,
        shadow: bool,
        text: str,
        font_family: str,
        font_size: int,
        bold: bool,
        text_shadow: bool,
        text_color: QColor,
    ):
        self._select_color(self._color_buttons, self.custom_color_btn, fill_color)

        shape_btn = self._shape_buttons.get(shape)
        if shape_btn is not None:
            shape_btn.setChecked(True)

        self.border_btn.blockSignals(True)
        self.border_btn.setChecked(border)
        self.border_btn.blockSignals(False)

        self.shadow_btn.blockSignals(True)
        self.shadow_btn.setChecked(shadow)
        self.shadow_btn.blockSignals(False)

        self.text_edit.blockSignals(True)
        self.text_edit.setText(text)
        self.text_edit.blockSignals(False)

        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentFont(QFont(font_family))
        self.font_combo.blockSignals(False)

        self.size_spin.blockSignals(True)
        self.size_spin.setValue(font_size)
        self.size_spin.blockSignals(False)

        self.bold_btn.blockSignals(True)
        self.bold_btn.setChecked(bold)
        self.bold_btn.blockSignals(False)

        self.text_shadow_btn.blockSignals(True)
        self.text_shadow_btn.setChecked(text_shadow)
        self.text_shadow_btn.blockSignals(False)

        text_color_btn = self._text_color_buttons.get(text_color.name())
        if text_color_btn is not None:
            text_color_btn.setChecked(True)


class TextPropertiesPanel(_IslandPanel):
    color_changed = Signal(QColor)
    font_changed = Signal(str)
    size_changed = Signal(int)
    bold_toggled = Signal(bool)
    shadow_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(18)

        outer.addLayout(self._build_color_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_font_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_bold_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_shadow_section())
        outer.addStretch(1)

    def _build_color_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("color"))
        row, self.color_group, self._color_buttons, self.custom_color_btn = self._color_row(
            TEXT_PALETTE, TEXT_PALETTE[0], self.color_changed.emit
        )
        self.custom_color_btn.clicked.connect(self._pick_custom_color)
        col.addLayout(row)
        return col

    def _build_font_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("font"))
        row = QHBoxLayout()
        row.setSpacing(8)

        self.font_combo = QFontComboBox()
        self.font_combo.setFixedWidth(150)
        self.font_combo.currentFontChanged.connect(lambda f: self.font_changed.emit(f.family()))
        row.addWidget(self.font_combo)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 96)
        self.size_spin.setValue(16)
        self.size_spin.setSuffix(" px")
        self.size_spin.setFixedWidth(70)
        self.size_spin.valueChanged.connect(self.size_changed.emit)
        row.addWidget(self.size_spin)

        col.addLayout(row)
        return col

    def _build_bold_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("bold"))
        self.bold_btn = QToolButton()
        self.bold_btn.setCheckable(True)
        self.bold_btn.setChecked(True)
        self.bold_btn.setFixedSize(38, 34)
        self.bold_btn.setIcon(icons.bold_icon())
        self.bold_btn.setIconSize(QSize(20, 20))
        self._tooltip(self.bold_btn, "bold")
        self.bold_btn.toggled.connect(self.bold_toggled.emit)
        col.addWidget(self.bold_btn)
        return col

    def _build_shadow_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("shadow"))
        self.shadow_btn = QToolButton()
        self.shadow_btn.setCheckable(True)
        self.shadow_btn.setFixedSize(38, 34)
        self.shadow_btn.setIcon(icons.text_shadow_icon())
        self.shadow_btn.setIconSize(QSize(22, 22))
        self._tooltip(self.shadow_btn, "text_shadow_tooltip")
        self.shadow_btn.toggled.connect(self.shadow_toggled.emit)
        col.addWidget(self.shadow_btn)
        return col

    def _pick_custom_color(self):
        color = QColorDialog.getColor(QColor("#1e1e1e"), self, tr("custom_color_text"))
        if color.isValid():
            self.custom_color_btn.setIcon(icons.circle_swatch_icon(color))
            self.custom_color_btn.setChecked(True)
            self.color_changed.emit(color)
        else:
            checked = self.color_group.checkedButton()
            if checked is None:
                self._color_buttons[TEXT_PALETTE[0].name()].setChecked(True)

    def sync_from(self, color: QColor, font_family: str, font_size: int, bold: bool, shadow: bool):
        self._select_color(self._color_buttons, self.custom_color_btn, color)

        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentFont(QFont(font_family))
        self.font_combo.blockSignals(False)

        self.size_spin.blockSignals(True)
        self.size_spin.setValue(font_size)
        self.size_spin.blockSignals(False)

        self.bold_btn.blockSignals(True)
        self.bold_btn.setChecked(bold)
        self.bold_btn.blockSignals(False)

        self.shadow_btn.blockSignals(True)
        self.shadow_btn.setChecked(shadow)
        self.shadow_btn.blockSignals(False)


class FramePropertiesPanel(_IslandPanel):
    color_changed = Signal(QColor)
    thickness_changed = Signal(float)
    rounded_toggled = Signal(bool)
    shadow_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(18)

        outer.addLayout(self._build_color_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_thickness_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_corner_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_shadow_section())
        outer.addStretch(1)

    def _build_color_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("color"))
        row, self.color_group, self._color_buttons, self.custom_color_btn = self._color_row(
            FRAME_PALETTE, FRAME_PALETTE[0], self.color_changed.emit
        )
        self.custom_color_btn.clicked.connect(self._pick_custom_color)
        col.addLayout(row)
        return col

    def _build_thickness_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("thickness"))
        row = QHBoxLayout()
        row.setSpacing(6)

        self.thickness_group = QButtonGroup(self)
        self.thickness_group.setExclusive(True)
        self._thickness_buttons = {}
        for key, value in THICKNESS_OPTIONS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setFixedSize(38, 34)
            btn.setIcon(icons.thickness_icon(value + 1))
            btn.setIconSize(QSize(26, 20))
            self._tooltip(btn, key)
            btn.clicked.connect(lambda _checked, v=value: self.thickness_changed.emit(v))
            self.thickness_group.addButton(btn)
            row.addWidget(btn)
            self._thickness_buttons[value] = btn
            if key == "thickness_medium":
                btn.setChecked(True)

        col.addLayout(row)
        return col

    def _build_corner_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("corners"))
        row = QHBoxLayout()
        row.setSpacing(6)

        self.corner_group = QButtonGroup(self)
        self.corner_group.setExclusive(True)
        self._corner_buttons = {}
        for key, rounded in CORNER_OPTIONS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setFixedSize(38, 34)
            btn.setIcon(icons.corner_style_icon(rounded))
            btn.setIconSize(QSize(24, 22))
            self._tooltip(btn, key)
            btn.clicked.connect(lambda _checked, r=rounded: self.rounded_toggled.emit(r))
            self.corner_group.addButton(btn)
            row.addWidget(btn)
            self._corner_buttons[rounded] = btn
            if not rounded:
                btn.setChecked(True)

        col.addLayout(row)
        return col

    def _build_shadow_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("shadow"))
        self.shadow_btn = QToolButton()
        self.shadow_btn.setCheckable(True)
        self.shadow_btn.setFixedSize(38, 34)
        self.shadow_btn.setIcon(icons.shadow_icon())
        self.shadow_btn.setIconSize(QSize(24, 24))
        self._tooltip(self.shadow_btn, "shadow_tooltip_frame")
        self.shadow_btn.toggled.connect(self.shadow_toggled.emit)
        col.addWidget(self.shadow_btn)
        return col

    def _pick_custom_color(self):
        color = QColorDialog.getColor(QColor("#e53935"), self, tr("custom_color_frame"))
        if color.isValid():
            self.custom_color_btn.setIcon(icons.circle_swatch_icon(color))
            self.custom_color_btn.setChecked(True)
            self.color_changed.emit(color)
        else:
            checked = self.color_group.checkedButton()
            if checked is None:
                self._color_buttons[FRAME_PALETTE[0].name()].setChecked(True)

    def sync_from(self, color: QColor, width: float, rounded: bool, shadow: bool):
        self._select_color(self._color_buttons, self.custom_color_btn, color)
        btn = self._thickness_buttons.get(width)
        if btn is not None:
            btn.setChecked(True)
        corner_btn = self._corner_buttons.get(rounded)
        if corner_btn is not None:
            corner_btn.setChecked(True)
        self.shadow_btn.blockSignals(True)
        self.shadow_btn.setChecked(shadow)
        self.shadow_btn.blockSignals(False)


class StickerPropertiesPanel(_IslandPanel):
    kind_changed = Signal(StickerKind)
    color_changed = Signal(QColor)
    size_changed = Signal(int)
    shadow_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(18)

        outer.addLayout(self._build_kind_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_color_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_size_section())
        outer.addWidget(self._vseparator())
        outer.addLayout(self._build_shadow_section())
        outer.addStretch(1)

    def _build_kind_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("sticker_kind_section"))
        row = QHBoxLayout()
        row.setSpacing(6)

        self.kind_group = QButtonGroup(self)
        self.kind_group.setExclusive(True)
        self._kind_buttons = {}
        for key, kind in STICKER_OPTIONS:
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setFixedSize(38, 34)
            btn.setIcon(icons.sticker_icon(kind))
            btn.setIconSize(QSize(26, 26))
            self._tooltip(btn, key)
            btn.clicked.connect(lambda _checked, k=kind: self.kind_changed.emit(k))
            self.kind_group.addButton(btn)
            row.addWidget(btn)
            self._kind_buttons[kind] = btn
            if kind == StickerKind.EXCLAMATION:
                btn.setChecked(True)

        col.addLayout(row)
        return col

    def _build_color_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("color"))
        row, self.color_group, self._color_buttons, self.custom_color_btn = self._color_row(
            STICKER_PALETTE, STICKER_PALETTE[0], self.color_changed.emit
        )
        self.custom_color_btn.clicked.connect(self._pick_custom_color)
        col.addLayout(row)
        return col

    def _build_size_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("size"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(16, 160)
        self.size_spin.setValue(48)
        self.size_spin.setSuffix(" px")
        self.size_spin.setFixedWidth(80)
        self.size_spin.valueChanged.connect(self.size_changed.emit)
        col.addWidget(self.size_spin)
        return col

    def _build_shadow_section(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("shadow"))
        self.shadow_btn = QToolButton()
        self.shadow_btn.setCheckable(True)
        self.shadow_btn.setFixedSize(38, 34)
        self.shadow_btn.setIcon(icons.shadow_icon())
        self.shadow_btn.setIconSize(QSize(24, 24))
        self._tooltip(self.shadow_btn, "shadow_tooltip_sticker")
        self.shadow_btn.toggled.connect(self.shadow_toggled.emit)
        col.addWidget(self.shadow_btn)
        return col

    def _pick_custom_color(self):
        color = QColorDialog.getColor(QColor("#e53935"), self, tr("custom_color_sticker"))
        if color.isValid():
            self.custom_color_btn.setIcon(icons.circle_swatch_icon(color))
            self.custom_color_btn.setChecked(True)
            self.color_changed.emit(color)
        else:
            checked = self.color_group.checkedButton()
            if checked is None:
                self._color_buttons[STICKER_PALETTE[0].name()].setChecked(True)

    def sync_from(self, kind: StickerKind, color: QColor, size: int, shadow: bool):
        kind_btn = self._kind_buttons.get(kind)
        if kind_btn is not None:
            kind_btn.setChecked(True)
        self._select_color(self._color_buttons, self.custom_color_btn, color)
        self.size_spin.blockSignals(True)
        self.size_spin.setValue(int(size))
        self.size_spin.blockSignals(False)
        self.shadow_btn.blockSignals(True)
        self.shadow_btn.setChecked(shadow)
        self.shadow_btn.blockSignals(False)


class BlurPropertiesPanel(_IslandPanel):
    pixel_size_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(18)

        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self._section_label("blur_intensity"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(4, 60)
        self.size_spin.setValue(14)
        self.size_spin.setSuffix(" px")
        self.size_spin.setFixedWidth(80)
        self.size_spin.valueChanged.connect(self.pixel_size_changed.emit)
        col.addWidget(self.size_spin)
        outer.addLayout(col)

        outer.addWidget(self._section_label("blur_hint"))
        outer.addStretch(1)

    def sync_from(self, pixel_size: int):
        self.size_spin.blockSignals(True)
        self.size_spin.setValue(int(pixel_size))
        self.size_spin.blockSignals(False)


class CropPropertiesPanel(_IslandPanel):
    apply_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 10, 18, 10)
        outer.setSpacing(12)

        outer.addWidget(self._section_label("crop_hint"))
        outer.addStretch(1)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("panelSecondaryButton")
        self._button_text(self.cancel_btn, "crop_cancel")
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        outer.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton()
        self.apply_btn.setObjectName("panelPrimaryButton")
        self._button_text(self.apply_btn, "crop_apply")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.apply_clicked.emit)
        outer.addWidget(self.apply_btn)

    def set_apply_enabled(self, enabled: bool):
        self.apply_btn.setEnabled(enabled)
