from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QCursor, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from .items import ArrowItem, FrameItem, SpeechBubbleItem, StickerItem, TextAnnotationItem
from .tools import ArrowStyle, BubbleShape, StickerKind, Tool


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

        self._drawing = False
        self._start_pos = QPointF()
        self._temp_item = None
        self.undo_stack = []

    def set_tool(self, tool: Tool):
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
        self.scene_.set_background_image(pixmap)
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
        if self.current_tool in (Tool.ARROW, Tool.BUBBLE, Tool.FRAME) and event.button() == Qt.MouseButton.LeftButton:
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

    def mouseMoveEvent(self, event):
        if self._drawing and self.current_tool in (Tool.ARROW, Tool.BUBBLE, Tool.FRAME):
            current = self.mapToScene(event.position().toPoint())
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
                rect = QRectF(self._start_pos, current).normalized()
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
            else:
                rect = QRectF(self._start_pos, current).normalized()
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
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drawing and event.button() == Qt.MouseButton.LeftButton:
            self._drawing = False
            if self._temp_item is not None:
                self._temp_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
                self._temp_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
                self.undo_stack.append(self._temp_item)
                self._temp_item = None
            return
        super().mouseReleaseEvent(event)

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
        self.undo_stack.append(text_item)

    def _add_sticker(self, pos: QPointF):
        sticker = StickerItem(
            self.sticker_kind,
            color=self.sticker_color,
            size=self.sticker_size,
            shadow=self.sticker_shadow,
        )
        sticker.setPos(pos)
        self.scene_.addItem(sticker)
        self.undo_stack.append(sticker)

    def undo(self):
        if self.undo_stack:
            item = self.undo_stack.pop()
            self.scene_.removeItem(item)

    def delete_selected(self):
        for item in self.scene_.selectedItems():
            self.scene_.removeItem(item)
            if item in self.undo_stack:
                self.undo_stack.remove(item)

    def export_image(self, path: str) -> bool:
        if self.scene_.background_item is None:
            return False
        rect = self.scene_.sceneRect()
        image = QPixmap(rect.size().toSize())
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        target = QRectF(0, 0, rect.width(), rect.height())
        self.scene_.render(painter, target, rect)
        painter.end()
        return image.save(path)
