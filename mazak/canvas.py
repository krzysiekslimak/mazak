from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QCursor, QImage, QKeySequence, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QGraphicsItem, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView

from .items import ArrowItem, BlurRegionItem, FrameItem, SpeechBubbleItem, StickerItem, TextAnnotationItem
from .tools import ArrowStyle, BubbleShape, StickerKind, Tool
from .undo import Command, CompositeCommand, UndoManager


class CanvasScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_item: QGraphicsPixmapItem | None = None

    def set_background_image(self, pixmap: QPixmap):
        if self.background_item:
            self.removeItem(self.background_item)
        self.background_item = QGraphicsPixmapItem(pixmap)
        self.background_item.setZValue(-1000)
        self.background_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.background_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.background_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.addItem(self.background_item)
        self.setSceneRect(QRectF(pixmap.rect()))


MIN_ZOOM = 0.1
MAX_ZOOM = 8.0


class CanvasView(QGraphicsView):
    zoom_changed = Signal(float)
    crop_pending_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_ = CanvasScene(self)
        self.setScene(self.scene_)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setBackgroundBrush(QBrush(QColor("#cfd4da")))
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._fit_mode = True

        self.current_tool = Tool.SELECT
        self.arrow_color = QColor("#e53935")
        self.arrow_thickness = 4
        self.arrow_style = ArrowStyle.CLASSIC
        self.arrow_shadow = False
        self.bubble_fill_color = QColor("#ffffff")
        self.bubble_border_color = QColor("#1e1e1e")
        self.bubble_shape = BubbleShape.ROUNDED
        self.bubble_border = False
        self.bubble_shadow = False
        self.bubble_text = "Tekst"
        self.bubble_font_family = ""
        self.bubble_font_size = 16
        self.bubble_bold = True
        self.bubble_text_shadow = False
        self.bubble_text_color = QColor("#1e1e1e")
        self.text_color = QColor("#1e1e1e")
        self.text_font_family = ""
        self.text_font_size = 16
        self.text_bold = True
        self.text_shadow = False
        self.frame_color = QColor("#e53935")
        self.frame_thickness = 4
        self.frame_rounded = False
        self.frame_shadow = False
        self.sticker_kind = StickerKind.EXCLAMATION
        self.sticker_color = QColor("#e53935")
        self.sticker_size = 48
        self.sticker_shadow = False
        self.blur_pixel_size = 14

        self._drawing = False
        self._start_pos = QPointF()
        self._temp_item = None
        self.undo_manager = UndoManager()

        self._crop_overlay: QGraphicsRectItem | None = None
        self._pending_crop_rect: QRectF | None = None

    def set_tool(self, tool: Tool):
        if self.current_tool == Tool.CROP and tool != Tool.CROP:
            self.cancel_crop()
        self.current_tool = tool
        if tool == Tool.SELECT:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene_.background_item is not None and self._fit_mode:
            self.fitInView(self.scene_.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._notify_zoom()

    def load_image(self, path: str):
        pixmap = QPixmap(path)
        self._load_pixmap(pixmap)

    def load_image_from_clipboard(self) -> bool:
        image = QApplication.clipboard().image()
        if image.isNull():
            return False
        self._load_pixmap(QPixmap.fromImage(image))
        return True

    def _load_pixmap(self, pixmap: QPixmap):
        self.scene_.set_background_image(pixmap)
        self.undo_manager.clear()
        self.cancel_crop()
        self._fit_mode = True
        self.fitInView(self.scene_.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._notify_zoom()

    def _notify_zoom(self):
        self.zoom_changed.emit(self.transform().m11())

    def current_zoom(self) -> float:
        return self.transform().m11()

    def zoom_fit(self):
        if self.scene_.background_item is None:
            return
        self._fit_mode = True
        self.fitInView(self.scene_.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._notify_zoom()

    def zoom_reset(self):
        if self.scene_.background_item is None:
            return
        self._fit_mode = False
        self.resetTransform()
        self._notify_zoom()

    def zoom_by(self, factor: float):
        if self.scene_.background_item is None:
            return
        new_zoom = self.current_zoom() * factor
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, new_zoom))
        factor = new_zoom / self.current_zoom()
        self._fit_mode = False
        self.scale(factor, factor)
        self._notify_zoom()

    def zoom_in(self):
        self.zoom_by(1.25)

    def zoom_out(self):
        self.zoom_by(0.8)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.zoom_by(factor)
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event):
        if self.current_tool in (Tool.ARROW, Tool.BUBBLE, Tool.FRAME, Tool.BLUR, Tool.CROP) and event.button() == Qt.MouseButton.LeftButton:
            self._drawing = True
            self._start_pos = self.mapToScene(event.position().toPoint())
            self._temp_item = None
            return
        if self.current_tool == Tool.TEXT and event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.position().toPoint())
            self._add_text(pos)
            return
        if self.current_tool == Tool.STICKER and event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.position().toPoint())
            self._add_sticker(pos)
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Paste):
            self.load_image_from_clipboard()
            event.accept()
            return
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_to_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drawing and self.current_tool in (Tool.ARROW, Tool.BUBBLE, Tool.FRAME, Tool.BLUR, Tool.CROP):
            current = self.mapToScene(event.position().toPoint())
            rect = QRectF(self._start_pos, current).normalized()

            if self.current_tool == Tool.ARROW:
                if self._temp_item is None:
                    self._temp_item = ArrowItem(
                        self._start_pos,
                        current,
                        self.arrow_color,
                        self.arrow_thickness,
                        self.arrow_style,
                        self.arrow_shadow,
                    )
                    self.scene_.addItem(self._temp_item)
                else:
                    self._temp_item.set_end(current)
            elif self.current_tool == Tool.BUBBLE:
                if self._temp_item is None:
                    self._temp_item = SpeechBubbleItem(
                        rect,
                        fill_color=self.bubble_fill_color,
                        border_color=self.bubble_border_color,
                        shape=self.bubble_shape,
                        border=self.bubble_border,
                        shadow=self.bubble_shadow,
                        text=self.bubble_text or "Tekst",
                        font_family=self.bubble_font_family,
                        font_size=self.bubble_font_size,
                        bold=self.bubble_bold,
                        text_shadow=self.bubble_text_shadow,
                        text_color=self.bubble_text_color,
                    )
                    self.scene_.addItem(self._temp_item)
                else:
                    self._temp_item.set_rect(rect)
            elif self.current_tool == Tool.FRAME:
                if self._temp_item is None:
                    self._temp_item = FrameItem(
                        rect,
                        color=self.frame_color,
                        width=self.frame_thickness,
                        rounded=self.frame_rounded,
                        shadow=self.frame_shadow,
                    )
                    self.scene_.addItem(self._temp_item)
                else:
                    self._temp_item.set_rect(rect)
            elif self.current_tool == Tool.BLUR:
                if self._temp_item is None:
                    self._temp_item = BlurRegionItem(rect, self._get_background_pixmap, self.blur_pixel_size)
                    self.scene_.addItem(self._temp_item)
                else:
                    self._temp_item.set_rect(rect)
            else:
                self._update_crop_overlay(rect)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drawing and event.button() == Qt.MouseButton.LeftButton:
            self._drawing = False
            if self.current_tool == Tool.CROP:
                if self._crop_overlay is not None:
                    self._pending_crop_rect = self._crop_overlay.rect()
                    self.crop_pending_changed.emit(True)
                self._temp_item = None
                return
            if self._temp_item is not None:
                item = self._temp_item
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
                self._push_add_command(item)
                self._temp_item = None
            return
        super().mouseReleaseEvent(event)

    def _get_background_pixmap(self) -> QPixmap | None:
        if self.scene_.background_item is None:
            return None
        return self.scene_.background_item.pixmap()

    def _update_crop_overlay(self, rect: QRectF):
        if self._crop_overlay is None:
            self._crop_overlay = QGraphicsRectItem()
            self._crop_overlay.setPen(QPen(QColor("#2f6fed"), 1.5, Qt.PenStyle.DashLine))
            self._crop_overlay.setBrush(QBrush(QColor(47, 111, 237, 40)))
            self._crop_overlay.setZValue(2000)
            self.scene_.addItem(self._crop_overlay)
        self._crop_overlay.setRect(rect)

    def cancel_crop(self):
        if self._crop_overlay is not None:
            self.scene_.removeItem(self._crop_overlay)
            self._crop_overlay = None
        self._pending_crop_rect = None
        self.crop_pending_changed.emit(False)

    def apply_crop(self):
        if self._pending_crop_rect is None or self.scene_.background_item is None:
            return
        crop_rect = self._pending_crop_rect.intersected(self.scene_.sceneRect()).toRect()
        if crop_rect.width() < 1 or crop_rect.height() < 1:
            return

        old_pixmap = self.scene_.background_item.pixmap()
        new_pixmap = old_pixmap.copy(crop_rect)
        offset = QPointF(-crop_rect.topLeft())
        new_scene_rect = QRectF(0, 0, crop_rect.width(), crop_rect.height())

        for item in list(self.scene_.items()):
            if item is self.scene_.background_item or item is self._crop_overlay:
                continue
            shifted_rect = item.sceneBoundingRect().translated(offset)
            if not new_scene_rect.intersects(shifted_rect):
                self.scene_.removeItem(item)
                continue
            item.setPos(item.pos() + offset)

        self.scene_.set_background_image(new_pixmap)
        self.undo_manager.clear()
        self.cancel_crop()
        self._fit_mode = True
        self.fitInView(self.scene_.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._notify_zoom()

    def _push_add_command(self, item):
        scene = self.scene_

        def do_add():
            scene.addItem(item)

        def do_remove():
            scene.removeItem(item)

        self.undo_manager.push(Command(undo_fn=do_remove, redo_fn=do_add))

    def _add_text(self, pos: QPointF):
        text_item = TextAnnotationItem(
            "Opis",
            color=self.text_color,
            font_family=self.text_font_family,
            font_size=self.text_font_size,
            bold=self.text_bold,
            shadow=self.text_shadow,
        )
        text_item.setPos(pos)
        self.scene_.addItem(text_item)
        text_item.setSelected(True)
        text_item.start_editing(select_all=True)
        self._push_add_command(text_item)

    def _add_sticker(self, pos: QPointF):
        sticker = StickerItem(
            self.sticker_kind,
            color=self.sticker_color,
            size=self.sticker_size,
            shadow=self.sticker_shadow,
        )
        sticker.setPos(pos)
        self.scene_.addItem(sticker)
        self._push_add_command(sticker)

    def undo(self):
        self.undo_manager.undo()

    def redo(self):
        self.undo_manager.redo()

    def delete_selected(self):
        selected = list(self.scene_.selectedItems())
        if not selected:
            return
        scene = self.scene_
        commands = []
        for item in selected:
            def do_remove(item=item):
                scene.removeItem(item)

            def do_add(item=item):
                scene.addItem(item)

            commands.append(Command(undo_fn=do_add, redo_fn=do_remove))
            scene.removeItem(item)
        self.undo_manager.push(CompositeCommand(commands))

    def _render_flat(self) -> QImage | None:
        if self.scene_.background_item is None:
            return None
        rect = self.scene_.sceneRect()
        image = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        target = QRectF(0, 0, rect.width(), rect.height())
        self.scene_.render(painter, target, rect)
        painter.end()
        return image

    def export_image(self, path: str) -> bool:
        image = self._render_flat()
        if image is None:
            return False
        return image.save(path)

    def copy_to_clipboard(self) -> bool:
        image = self._render_flat()
        if image is None:
            return False
        QApplication.clipboard().setImage(image)
        return True
