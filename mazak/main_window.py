import os

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import QFileDialog, QLabel, QMainWindow, QMessageBox, QToolBar, QVBoxLayout, QWidget

from . import icons
from .canvas import CanvasView
from .items import ArrowItem, BlurRegionItem, FrameItem, SpeechBubbleItem, StickerItem, TextAnnotationItem
from .panels import (
    ArrowPropertiesPanel,
    BlurPropertiesPanel,
    BubblePropertiesPanel,
    CropPropertiesPanel,
    FramePropertiesPanel,
    StickerPropertiesPanel,
    TextPropertiesPanel,
)
from .style import APP_STYLESHEET
from .tools import StickerKind, Tool
from .undo import Command


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mazak")
        self.setWindowIcon(icons.app_icon())
        self.resize(1100, 750)
        self.setStyleSheet(APP_STYLESHEET)

        self.settings = QSettings("Mazak", "Mazak")

        self.view = CanvasView(self)

        self.arrow_panel = ArrowPropertiesPanel(self)
        self.arrow_panel.color_changed.connect(self._set_arrow_color)
        self.arrow_panel.thickness_changed.connect(self._set_arrow_thickness)
        self.arrow_panel.style_changed.connect(self._set_arrow_style)
        self.arrow_panel.shadow_toggled.connect(self._set_arrow_shadow)

        self.bubble_panel = BubblePropertiesPanel(self)
        self.bubble_panel.color_changed.connect(self._set_bubble_color)
        self.bubble_panel.shape_changed.connect(self._set_bubble_shape)
        self.bubble_panel.border_toggled.connect(self._set_bubble_border)
        self.bubble_panel.shadow_toggled.connect(self._set_bubble_shadow)
        self.bubble_panel.text_changed.connect(self._set_bubble_text)
        self.bubble_panel.font_changed.connect(self._set_bubble_font)
        self.bubble_panel.bold_toggled.connect(self._set_bubble_bold)
        self.bubble_panel.size_changed.connect(self._set_bubble_size)
        self.bubble_panel.text_shadow_toggled.connect(self._set_bubble_text_shadow)
        self.bubble_panel.text_color_changed.connect(self._set_bubble_text_color)
        self.bubble_panel.setVisible(False)

        self.text_panel = TextPropertiesPanel(self)
        self.text_panel.color_changed.connect(self._set_text_color)
        self.text_panel.font_changed.connect(self._set_text_font)
        self.text_panel.size_changed.connect(self._set_text_size)
        self.text_panel.bold_toggled.connect(self._set_text_bold)
        self.text_panel.shadow_toggled.connect(self._set_text_shadow)
        self.text_panel.setVisible(False)

        self.frame_panel = FramePropertiesPanel(self)
        self.frame_panel.color_changed.connect(self._set_frame_color)
        self.frame_panel.thickness_changed.connect(self._set_frame_thickness)
        self.frame_panel.rounded_toggled.connect(self._set_frame_rounded)
        self.frame_panel.shadow_toggled.connect(self._set_frame_shadow)
        self.frame_panel.setVisible(False)

        self.sticker_panel = StickerPropertiesPanel(self)
        self.sticker_panel.kind_changed.connect(self._set_sticker_kind)
        self.sticker_panel.color_changed.connect(self._set_sticker_color)
        self.sticker_panel.size_changed.connect(self._set_sticker_size)
        self.sticker_panel.shadow_toggled.connect(self._set_sticker_shadow)
        self.sticker_panel.setVisible(False)

        self.blur_panel = BlurPropertiesPanel(self)
        self.blur_panel.pixel_size_changed.connect(self._set_blur_pixel_size)
        self.blur_panel.setVisible(False)

        self.crop_panel = CropPropertiesPanel(self)
        self.crop_panel.apply_clicked.connect(self._apply_crop)
        self.crop_panel.cancel_clicked.connect(self._cancel_crop)
        self.view.crop_pending_changed.connect(self.crop_panel.set_apply_enabled)
        self.crop_panel.setVisible(False)

        self._panels = (
            self.arrow_panel,
            self.bubble_panel,
            self.text_panel,
            self.frame_panel,
            self.sticker_panel,
            self.blur_panel,
            self.crop_panel,
        )

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        panel_wrap = QWidget(self)
        panel_wrap_layout = QVBoxLayout(panel_wrap)
        panel_wrap_layout.setContentsMargins(12, 10, 12, 10)
        for panel in self._panels:
            panel_wrap_layout.addWidget(panel)
        self.panel_wrap = panel_wrap
        self.panel_wrap.setVisible(False)

        layout.addWidget(panel_wrap)
        layout.addWidget(self.view)
        self.setCentralWidget(container)

        self.current_path = None
        self._selected_item = None
        self.view.scene_.selectionChanged.connect(self._refresh_panels)
        self._build_toolbar()

        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("color: #5f6368; padding-right: 6px;")
        self.statusBar().addPermanentWidget(self.zoom_label)
        self.view.zoom_changed.connect(self._update_zoom_label)

        self.statusBar().showMessage("Otwórz obraz, żeby zacząć adnotować")
        self.view.setFocus()

    def _update_zoom_label(self, zoom: float):
        self.zoom_label.setText(f"{round(zoom * 100)}%")

    def _build_toolbar(self):
        toolbar = QToolBar("Narzędzia")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(26, 26))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)

        open_action = QAction(icons.open_icon(), "Otwórz", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setToolTip("Otwórz obraz (Ctrl+O)")
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)

        paste_action = QAction(icons.paste_icon(), "Wklej", self)
        paste_action.setToolTip("Wklej obraz ze schowka (Ctrl+V, gdy płótno ma fokus)")
        paste_action.triggered.connect(self.paste_image)
        toolbar.addAction(paste_action)

        export_action = QAction(icons.export_icon(), "Eksportuj", self)
        export_action.setShortcut(QKeySequence.StandardKey.Save)
        export_action.setToolTip("Eksportuj jako PNG (Ctrl+S)")
        export_action.triggered.connect(self.export_image)
        toolbar.addAction(export_action)

        copy_action = QAction(icons.copy_icon(), "Kopiuj", self)
        copy_action.setToolTip("Kopiuj wynik do schowka (Ctrl+C, gdy płótno ma fokus)")
        copy_action.triggered.connect(self.copy_image)
        toolbar.addAction(copy_action)

        toolbar.addSeparator()

        tool_group = QActionGroup(self)
        tool_group.setExclusive(True)

        def add_tool_action(label, icon, tool, checked=False):
            action = QAction(icon, label, self)
            action.setCheckable(True)
            action.setChecked(checked)
            action.triggered.connect(lambda: self._activate_tool(tool))
            tool_group.addAction(action)
            toolbar.addAction(action)
            return action

        add_tool_action("Zaznacz", icons.select_icon(), Tool.SELECT, checked=True)
        add_tool_action("Strzałka", icons.arrow_icon(), Tool.ARROW)
        add_tool_action("Dymek", icons.bubble_icon(), Tool.BUBBLE)
        add_tool_action("Tekst", icons.text_icon(), Tool.TEXT)
        add_tool_action("Ramka", icons.frame_icon(), Tool.FRAME)
        add_tool_action("Naklejki", icons.sticker_icon(StickerKind.EXCLAMATION), Tool.STICKER)
        add_tool_action("Rozmyj", icons.blur_icon(), Tool.BLUR)
        add_tool_action("Przytnij", icons.crop_icon(), Tool.CROP)

        toolbar.addSeparator()

        delete_action = QAction(icons.delete_icon(), "Usuń", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.setToolTip("Usuń zaznaczone (Delete)")
        delete_action.triggered.connect(self.view.delete_selected)
        toolbar.addAction(delete_action)

        undo_action = QAction(icons.undo_icon(), "Cofnij", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setToolTip("Cofnij (Ctrl+Z)")
        undo_action.triggered.connect(self.view.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction(icons.redo_icon(), "Ponów", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setToolTip("Ponów (Ctrl+Shift+Z)")
        redo_action.triggered.connect(self.view.redo)
        toolbar.addAction(redo_action)

        toolbar.addSeparator()

        zoom_out_action = QAction(icons.zoom_out_icon(), "Pomniejsz", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.setToolTip("Pomniejsz (Ctrl+Scroll / Ctrl+-)")
        zoom_out_action.triggered.connect(self.view.zoom_out)
        toolbar.addAction(zoom_out_action)

        zoom_in_action = QAction(icons.zoom_in_icon(), "Powiększ", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.setToolTip("Powiększ (Ctrl+Scroll / Ctrl++)")
        zoom_in_action.triggered.connect(self.view.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_fit_action = QAction(icons.zoom_fit_icon(), "Dopasuj", self)
        zoom_fit_action.setToolTip("Dopasuj do okna")
        zoom_fit_action.triggered.connect(self.view.zoom_fit)
        toolbar.addAction(zoom_fit_action)

    def _activate_tool(self, tool: Tool):
        self.view.set_tool(tool)
        self.view.scene_.clearSelection()
        self._refresh_panels()

    def _refresh_panels(self):
        selected = self.view.scene_.selectedItems()
        single = selected[0] if len(selected) == 1 else None

        if isinstance(single, ArrowItem):
            self._selected_item = single
            self.arrow_panel.sync_from(single.color, single.width, single.style, single.shadow_enabled)
            self._show_only(self.arrow_panel)
        elif isinstance(single, SpeechBubbleItem):
            self._selected_item = single
            self.bubble_panel.sync_from(
                single.fill_color,
                single.shape,
                single.border_enabled,
                single.shadow_enabled,
                single.text,
                single.font_family,
                single.font_size,
                single.bold,
                single.text_shadow_enabled,
                single.text_color,
            )
            self._show_only(self.bubble_panel)
        elif isinstance(single, TextAnnotationItem):
            self._selected_item = single
            self.text_panel.sync_from(single.color, single.font_family, single.font_size, single.bold, single.shadow_enabled)
            self._show_only(self.text_panel)
        elif isinstance(single, FrameItem):
            self._selected_item = single
            self.frame_panel.sync_from(single.color, single.width, single.rounded, single.shadow_enabled)
            self._show_only(self.frame_panel)
        elif isinstance(single, StickerItem):
            self._selected_item = single
            self.sticker_panel.sync_from(single.kind, single.color, single.size, single.shadow_enabled)
            self._show_only(self.sticker_panel)
        elif isinstance(single, BlurRegionItem):
            self._selected_item = single
            self.blur_panel.sync_from(single.pixel_size)
            self._show_only(self.blur_panel)
        else:
            self._selected_item = None
            tool = self.view.current_tool
            panel_by_tool = {
                Tool.ARROW: self.arrow_panel,
                Tool.BUBBLE: self.bubble_panel,
                Tool.TEXT: self.text_panel,
                Tool.FRAME: self.frame_panel,
                Tool.STICKER: self.sticker_panel,
                Tool.BLUR: self.blur_panel,
                Tool.CROP: self.crop_panel,
            }
            self._show_only(panel_by_tool.get(tool))

    def _show_only(self, panel_to_show):
        for panel in self._panels:
            panel.setVisible(panel is panel_to_show)
        self.panel_wrap.setVisible(panel_to_show is not None)

    def _push_property_edit(self, setter, old_value, new_value):
        if old_value == new_value:
            return
        self.view.undo_manager.push(Command(undo_fn=lambda: setter(old_value), redo_fn=lambda: setter(new_value)))

    def _set_arrow_color(self, color):
        self.view.arrow_color = color
        item = self._selected_item
        if isinstance(item, ArrowItem):
            old = item.color
            item.set_color(color)
            self._push_property_edit(item.set_color, old, color)

    def _set_arrow_thickness(self, value: float):
        self.view.arrow_thickness = value
        item = self._selected_item
        if isinstance(item, ArrowItem):
            old = item.width
            item.set_width(value)
            self._push_property_edit(item.set_width, old, value)

    def _set_arrow_style(self, style):
        self.view.arrow_style = style
        item = self._selected_item
        if isinstance(item, ArrowItem):
            old = item.style
            item.set_style(style)
            self._push_property_edit(item.set_style, old, style)

    def _set_arrow_shadow(self, enabled: bool):
        self.view.arrow_shadow = enabled
        item = self._selected_item
        if isinstance(item, ArrowItem):
            old = item.shadow_enabled
            item.set_shadow(enabled)
            self._push_property_edit(item.set_shadow, old, enabled)

    def _set_bubble_color(self, color):
        self.view.bubble_fill_color = color
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.fill_color
            item.set_fill_color(color)
            self._push_property_edit(item.set_fill_color, old, color)

    def _set_bubble_shape(self, shape):
        self.view.bubble_shape = shape
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.shape
            item.set_shape(shape)
            self._push_property_edit(item.set_shape, old, shape)

    def _set_bubble_border(self, enabled: bool):
        self.view.bubble_border = enabled
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.border_enabled
            item.set_border(enabled)
            self._push_property_edit(item.set_border, old, enabled)

    def _set_bubble_shadow(self, enabled: bool):
        self.view.bubble_shadow = enabled
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.shadow_enabled
            item.set_shadow(enabled)
            self._push_property_edit(item.set_shadow, old, enabled)

    def _set_bubble_text(self, text: str):
        self.view.bubble_text = text
        if isinstance(self._selected_item, SpeechBubbleItem):
            self._selected_item.set_text(text)

    def _set_bubble_font(self, family: str):
        self.view.bubble_font_family = family
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.font_family

            def setter(value, size=item.font_size, bold=item.bold):
                item.set_font(value, size, bold)

            item.set_font(family, item.font_size, item.bold)
            self._push_property_edit(setter, old, family)

    def _set_bubble_bold(self, enabled: bool):
        self.view.bubble_bold = enabled
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.bold

            def setter(value, family=item.font_family, size=item.font_size):
                item.set_font(family, size, value)

            item.set_font(item.font_family, item.font_size, enabled)
            self._push_property_edit(setter, old, enabled)

    def _set_bubble_size(self, size: int):
        self.view.bubble_font_size = size
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.font_size

            def setter(value, family=item.font_family, bold=item.bold):
                item.set_font(family, value, bold)

            item.set_font(item.font_family, size, item.bold)
            self._push_property_edit(setter, old, size)

    def _set_bubble_text_shadow(self, enabled: bool):
        self.view.bubble_text_shadow = enabled
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.text_shadow_enabled
            item.set_text_shadow(enabled)
            self._push_property_edit(item.set_text_shadow, old, enabled)

    def _set_bubble_text_color(self, color):
        self.view.bubble_text_color = color
        item = self._selected_item
        if isinstance(item, SpeechBubbleItem):
            old = item.text_color
            item.set_text_color(color)
            self._push_property_edit(item.set_text_color, old, color)

    def _set_text_color(self, color):
        self.view.text_color = color
        item = self._selected_item
        if isinstance(item, TextAnnotationItem):
            old = item.color
            item.set_color(color)
            self._push_property_edit(item.set_color, old, color)

    def _set_text_font(self, family: str):
        self.view.text_font_family = family
        item = self._selected_item
        if isinstance(item, TextAnnotationItem):
            old = item.font_family

            def setter(value, size=item.font_size, bold=item.bold):
                item.set_font(value, size, bold)

            item.set_font(family, item.font_size, item.bold)
            self._push_property_edit(setter, old, family)

    def _set_text_size(self, size: int):
        self.view.text_font_size = size
        item = self._selected_item
        if isinstance(item, TextAnnotationItem):
            old = item.font_size

            def setter(value, family=item.font_family, bold=item.bold):
                item.set_font(family, value, bold)

            item.set_font(item.font_family, size, item.bold)
            self._push_property_edit(setter, old, size)

    def _set_text_bold(self, enabled: bool):
        self.view.text_bold = enabled
        item = self._selected_item
        if isinstance(item, TextAnnotationItem):
            old = item.bold

            def setter(value, family=item.font_family, size=item.font_size):
                item.set_font(family, size, value)

            item.set_font(item.font_family, item.font_size, enabled)
            self._push_property_edit(setter, old, enabled)

    def _set_text_shadow(self, enabled: bool):
        self.view.text_shadow = enabled
        item = self._selected_item
        if isinstance(item, TextAnnotationItem):
            old = item.shadow_enabled
            item.set_shadow(enabled)
            self._push_property_edit(item.set_shadow, old, enabled)

    def _set_frame_color(self, color):
        self.view.frame_color = color
        item = self._selected_item
        if isinstance(item, FrameItem):
            old = item.color
            item.set_color(color)
            self._push_property_edit(item.set_color, old, color)

    def _set_frame_thickness(self, value: float):
        self.view.frame_thickness = value
        item = self._selected_item
        if isinstance(item, FrameItem):
            old = item.width
            item.set_width(value)
            self._push_property_edit(item.set_width, old, value)

    def _set_frame_rounded(self, enabled: bool):
        self.view.frame_rounded = enabled
        item = self._selected_item
        if isinstance(item, FrameItem):
            old = item.rounded
            item.set_rounded(enabled)
            self._push_property_edit(item.set_rounded, old, enabled)

    def _set_frame_shadow(self, enabled: bool):
        self.view.frame_shadow = enabled
        item = self._selected_item
        if isinstance(item, FrameItem):
            old = item.shadow_enabled
            item.set_shadow(enabled)
            self._push_property_edit(item.set_shadow, old, enabled)

    def _set_sticker_kind(self, kind):
        self.view.sticker_kind = kind
        item = self._selected_item
        if isinstance(item, StickerItem):
            old = item.kind
            item.set_kind(kind)
            self._push_property_edit(item.set_kind, old, kind)

    def _set_sticker_color(self, color):
        self.view.sticker_color = color
        item = self._selected_item
        if isinstance(item, StickerItem):
            old = item.color
            item.set_color(color)
            self._push_property_edit(item.set_color, old, color)

    def _set_sticker_size(self, size: int):
        self.view.sticker_size = size
        item = self._selected_item
        if isinstance(item, StickerItem):
            old = item.size
            item.set_size(size)
            self._push_property_edit(item.set_size, old, size)

    def _set_sticker_shadow(self, enabled: bool):
        self.view.sticker_shadow = enabled
        item = self._selected_item
        if isinstance(item, StickerItem):
            old = item.shadow_enabled
            item.set_shadow(enabled)
            self._push_property_edit(item.set_shadow, old, enabled)

    def _set_blur_pixel_size(self, size: int):
        self.view.blur_pixel_size = size
        item = self._selected_item
        if isinstance(item, BlurRegionItem):
            old = item.pixel_size
            item.set_pixel_size(size)
            self._push_property_edit(item.set_pixel_size, old, size)

    def _apply_crop(self):
        self.view.apply_crop()

    def _cancel_crop(self):
        self.view.cancel_crop()

    def open_image(self):
        start_dir = self.settings.value("last_open_dir", "", str)
        path, _ = QFileDialog.getOpenFileName(self, "Otwórz obraz", start_dir, "Obrazy (*.png *.jpg *.jpeg)")
        if path:
            self.view.load_image(path)
            self.current_path = path
            self.settings.setValue("last_open_dir", os.path.dirname(path))
            self.statusBar().showMessage(f"Wczytano: {path}")

    def paste_image(self):
        if self.view.load_image_from_clipboard():
            self.current_path = None
            self.statusBar().showMessage("Wklejono obraz ze schowka")
        else:
            QMessageBox.information(self, "Mazak", "Schowek nie zawiera obrazu.")

    def copy_image(self):
        if self.view.scene_.background_item is None:
            QMessageBox.warning(self, "Mazak", "Najpierw otwórz obraz.")
            return
        if self.view.copy_to_clipboard():
            self.statusBar().showMessage("Skopiowano wynik do schowka")

    def export_image(self):
        if self.view.scene_.background_item is None:
            QMessageBox.warning(self, "Mazak", "Najpierw otwórz obraz.")
            return
        start_dir = self.settings.value("last_export_dir", "", str)
        path, _ = QFileDialog.getSaveFileName(self, "Eksportuj jako PNG", start_dir, "PNG (*.png)")
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            if self.view.export_image(path):
                self.settings.setValue("last_export_dir", os.path.dirname(path))
                self.statusBar().showMessage(f"Zapisano: {path}")
            else:
                QMessageBox.critical(self, "Mazak", "Nie udało się zapisać pliku.")
