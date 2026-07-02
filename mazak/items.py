import math

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF, QTextOption
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsItem, QGraphicsPathItem, QGraphicsTextItem

from .tools import ArrowStyle, BubbleShape, StickerKind


class ArrowItem(QGraphicsPathItem):
    def __init__(
        self,
        start: QPointF,
        end: QPointF,
        color=QColor("#e53935"),
        width=4,
        style: ArrowStyle = ArrowStyle.CLASSIC,
        shadow: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._start = start
        self._end = end
        self._color = color
        self._width = width
        self._style = style
        self.set_shadow(shadow)
        self._update_path()

    def set_end(self, end: QPointF):
        self._end = end
        self._update_path()

    def set_color(self, color: QColor):
        self._color = color
        self._update_path()

    def set_width(self, width: float):
        self._width = width
        self._update_path()

    def set_style(self, style: ArrowStyle):
        self._style = style
        self._update_path()

    def set_shadow(self, enabled: bool):
        if enabled:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(16)
            effect.setOffset(3, 5)
            effect.setColor(QColor(0, 0, 0, 140))
            self.setGraphicsEffect(effect)
        else:
            self.setGraphicsEffect(None)

    @property
    def color(self) -> QColor:
        return self._color

    @property
    def width(self) -> float:
        return self._width

    @property
    def style(self) -> ArrowStyle:
        return self._style

    @property
    def shadow_enabled(self) -> bool:
        return self.graphicsEffect() is not None

    def _update_path(self):
        path = QPainterPath()
        line_vec = self._end - self._start
        length = math.hypot(line_vec.x(), line_vec.y())
        angle = math.atan2(line_vec.y(), line_vec.x()) if length else 0.0

        if self._style == ArrowStyle.SLIM:
            pen_width = max(1.5, self._width * 0.6)
            arrow_size = max(10, pen_width * 4)
            head_spread = math.pi / 6

            self.setPen(QPen(self._color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            self.setBrush(Qt.BrushStyle.NoBrush)

            path.moveTo(self._start)
            path.lineTo(self._end)

            p1 = QPointF(
                self._end.x() - math.cos(angle - head_spread) * arrow_size,
                self._end.y() - math.sin(angle - head_spread) * arrow_size,
            )
            p2 = QPointF(
                self._end.x() - math.cos(angle + head_spread) * arrow_size,
                self._end.y() - math.sin(angle + head_spread) * arrow_size,
            )
            path.moveTo(p1)
            path.lineTo(self._end)
            path.lineTo(p2)

        elif self._style == ArrowStyle.BOLD:
            pen_width = self._width * 1.6
            arrow_size = max(20, pen_width * 2.6)
            head_spread = math.pi / 5.5

            self.setPen(QPen(self._color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            self.setBrush(QBrush(self._color))

            back = QPointF(
                self._end.x() - math.cos(angle) * arrow_size * 0.55,
                self._end.y() - math.sin(angle) * arrow_size * 0.55,
            )
            path.moveTo(self._start)
            path.lineTo(back)

            p1 = QPointF(
                self._end.x() - math.cos(angle - head_spread) * arrow_size,
                self._end.y() - math.sin(angle - head_spread) * arrow_size,
            )
            p2 = QPointF(
                self._end.x() - math.cos(angle + head_spread) * arrow_size,
                self._end.y() - math.sin(angle + head_spread) * arrow_size,
            )
            path.addPolygon(QPolygonF([self._end, p1, p2]))
            path.closeSubpath()

        else:
            pen_width = self._width
            arrow_size = max(14, pen_width * 4)
            head_spread = math.pi / 7

            self.setPen(QPen(self._color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            self.setBrush(QBrush(self._color))

            back = QPointF(
                self._end.x() - math.cos(angle) * arrow_size * 0.6,
                self._end.y() - math.sin(angle) * arrow_size * 0.6,
            )
            path.moveTo(self._start)
            path.lineTo(back)

            p1 = QPointF(
                self._end.x() - math.cos(angle - head_spread) * arrow_size,
                self._end.y() - math.sin(angle - head_spread) * arrow_size,
            )
            p2 = QPointF(
                self._end.x() - math.cos(angle + head_spread) * arrow_size,
                self._end.y() - math.sin(angle + head_spread) * arrow_size,
            )
            path.addPolygon(QPolygonF([self._end, p1, p2]))
            path.closeSubpath()

        self.setPath(path)


class SpeechBubbleItem(QGraphicsPathItem):
    def __init__(
        self,
        rect: QRectF,
        fill_color=QColor("#ffffff"),
        border_color=QColor("#1e1e1e"),
        shape: BubbleShape = BubbleShape.ROUNDED,
        border: bool = False,
        shadow: bool = False,
        text: str = "Tekst",
        font_family: str = "",
        font_size: int = 16,
        bold: bool = True,
        text_shadow: bool = False,
        text_color=QColor("#1e1e1e"),
        parent=None,
    ):
        super().__init__(parent)
        self._rect = rect
        self._fill_color = fill_color
        self._border_color = border_color
        self._shape = shape
        self._border = border

        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(text_color)
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        text_option = QTextOption(Qt.AlignmentFlag.AlignHCenter)
        text_option.setWrapMode(QTextOption.WrapMode.WordWrap)
        self.text_item.document().setDefaultTextOption(text_option)
        self.set_font(font_family, font_size, bold)
        self.set_text_shadow(text_shadow)

        self.set_shadow(shadow)
        self._update_pen_brush()
        self._update_path()

    def set_rect(self, rect: QRectF):
        self._rect = rect
        self._update_path()

    def set_shape(self, shape: BubbleShape):
        self._shape = shape
        self._update_path()

    def set_border(self, enabled: bool):
        self._border = enabled
        self._update_pen_brush()

    def set_fill_color(self, color: QColor):
        self._fill_color = color
        self._update_pen_brush()

    def set_text_color(self, color: QColor):
        self.text_item.setDefaultTextColor(color)

    def set_shadow(self, enabled: bool):
        if enabled:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(18)
            effect.setOffset(3, 6)
            effect.setColor(QColor(0, 0, 0, 130))
            self.setGraphicsEffect(effect)
        else:
            self.setGraphicsEffect(None)

    def set_font(self, family: str, size: int, bold: bool):
        font = QFont(family) if family else self.text_item.font()
        font.setPointSize(size)
        font.setBold(bold)
        self.text_item.setFont(font)
        if self._rect.isValid():
            self._update_path()

    def set_text_shadow(self, enabled: bool):
        if enabled:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(6)
            effect.setOffset(1.5, 1.5)
            effect.setColor(QColor(0, 0, 0, 160))
            self.text_item.setGraphicsEffect(effect)
        else:
            self.text_item.setGraphicsEffect(None)

    def set_text(self, text: str):
        self.text_item.setPlainText(text)

    @property
    def fill_color(self) -> QColor:
        return self._fill_color

    @property
    def shape(self) -> BubbleShape:
        return self._shape

    @property
    def border_enabled(self) -> bool:
        return self._border

    @property
    def shadow_enabled(self) -> bool:
        return self.graphicsEffect() is not None

    @property
    def text(self) -> str:
        return self.text_item.toPlainText()

    @property
    def font_family(self) -> str:
        return self.text_item.font().family()

    @property
    def font_size(self) -> int:
        return self.text_item.font().pointSize()

    @property
    def bold(self) -> bool:
        return self.text_item.font().bold()

    @property
    def text_shadow_enabled(self) -> bool:
        return self.text_item.graphicsEffect() is not None

    @property
    def text_color(self) -> QColor:
        return self.text_item.defaultTextColor()

    def _update_pen_brush(self):
        self.setPen(QPen(self._border_color, 3) if self._border else QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(self._fill_color))

    def _ellipse_bottom_point(self, r: QRectF, t: float) -> QPointF:
        cx, cy = r.center().x(), r.center().y()
        a, b = r.width() / 2, r.height() / 2
        dx = (t - 0.5) * r.width()
        ratio = max(-1.0, min(1.0, dx / a)) if a else 0.0
        dy = b * math.sqrt(max(0.0, 1 - ratio**2))
        return QPointF(cx + dx, cy + dy)

    def _cloud_path(self, r: QRectF) -> QPainterPath:
        path = QPainterPath()
        inset = min(r.width(), r.height()) * 0.16
        body_rect = r.adjusted(inset, inset, -inset, -inset)
        path.addRoundedRect(body_rect, body_rect.height() * 0.3, body_rect.height() * 0.3)

        bump_r = min(r.width(), r.height()) * 0.22
        positions = [
            QPointF(r.left() + r.width() * 0.22, r.top() + bump_r * 0.6),
            QPointF(r.left() + r.width() * 0.5, r.top() + bump_r * 0.35),
            QPointF(r.left() + r.width() * 0.78, r.top() + bump_r * 0.6),
            QPointF(r.left() + bump_r * 0.55, r.top() + r.height() * 0.5),
            QPointF(r.right() - bump_r * 0.55, r.top() + r.height() * 0.5),
            QPointF(r.left() + r.width() * 0.25, r.bottom() - bump_r * 0.6),
            QPointF(r.left() + r.width() * 0.55, r.bottom() - bump_r * 0.35),
            QPointF(r.left() + r.width() * 0.82, r.bottom() - bump_r * 0.6),
        ]
        for pos in positions:
            bump = QPainterPath()
            bump.addEllipse(pos, bump_r, bump_r)
            path = path.united(bump)

        tail_r1 = bump_r * 0.4
        tail_r2 = bump_r * 0.22
        tail1_c = QPointF(r.left() + r.width() * 0.18, r.bottom() + tail_r1 * 0.7)
        tail2_c = QPointF(r.left() + r.width() * 0.08, r.bottom() + tail_r1 * 1.9)
        path.addEllipse(tail1_c, tail_r1, tail_r1)
        path.addEllipse(tail2_c, tail_r2, tail_r2)
        return path

    def _update_path(self):
        r = self._rect

        if self._shape == BubbleShape.OVAL:
            path = QPainterPath()
            path.addEllipse(r)
            tail_base1 = self._ellipse_bottom_point(r, 0.26)
            tail_base2 = self._ellipse_bottom_point(r, 0.42)
            tail_tip = QPointF(r.left() + r.width() * 0.16, r.bottom() + r.height() * 0.35)
            path.addPolygon(QPolygonF([tail_base1, tail_tip, tail_base2]))
            margin = max(14, r.width() * 0.12)
            text_rect = r

        elif self._shape == BubbleShape.CLOUD:
            path = self._cloud_path(r)
            inset = min(r.width(), r.height()) * 0.16
            text_rect = r.adjusted(inset, inset, -inset, -inset)
            margin = max(10, text_rect.width() * 0.1)

        else:
            path = QPainterPath()
            path.addRoundedRect(r, 16, 16)
            tail_base1 = QPointF(r.left() + r.width() * 0.2, r.bottom())
            tail_base2 = QPointF(r.left() + r.width() * 0.35, r.bottom())
            tail_tip = QPointF(r.left() + r.width() * 0.15, r.bottom() + 30)
            path.addPolygon(QPolygonF([tail_base1, tail_tip, tail_base2]))
            margin = 12
            text_rect = r

        self.setPath(path)
        avail_width = max(20, text_rect.width() - 2 * margin)
        self.text_item.setTextWidth(avail_width)

        doc_height = self.text_item.document().size().height()
        avail_height = max(0, text_rect.height() - 2 * margin)
        y = text_rect.top() + margin + max(0, (avail_height - doc_height) / 2)
        self.text_item.setPos(text_rect.left() + margin, y)

    def mouseDoubleClickEvent(self, event):
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.setFocus()
        cursor = self.text_item.textCursor()
        cursor.select(cursor.SelectionType.Document)
        self.text_item.setTextCursor(cursor)
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged and not value:
            self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        return super().itemChange(change, value)


class TextAnnotationItem(QGraphicsTextItem):
    def __init__(
        self,
        text: str = "Opis",
        color=QColor("#1e1e1e"),
        font_family: str = "",
        font_size: int = 16,
        bold: bool = True,
        shadow: bool = False,
        parent=None,
    ):
        super().__init__(text, parent)
        self.setDefaultTextColor(color)
        self.set_font(font_family, font_size, bold)
        self.set_shadow(shadow)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
        )
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    def start_editing(self, select_all: bool = False):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        if select_all:
            cursor = self.textCursor()
            cursor.select(cursor.SelectionType.Document)
            self.setTextCursor(cursor)

    def set_color(self, color: QColor):
        self.setDefaultTextColor(color)

    def set_font(self, family: str, size: int, bold: bool):
        font = QFont(family) if family else self.font()
        font.setPointSize(size)
        font.setBold(bold)
        self.setFont(font)

    def set_shadow(self, enabled: bool):
        if enabled:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(6)
            effect.setOffset(1.5, 1.5)
            effect.setColor(QColor(0, 0, 0, 160))
            self.setGraphicsEffect(effect)
        else:
            self.setGraphicsEffect(None)

    @property
    def color(self) -> QColor:
        return self.defaultTextColor()

    @property
    def font_family(self) -> str:
        return self.font().family()

    @property
    def font_size(self) -> int:
        return self.font().pointSize()

    @property
    def bold(self) -> bool:
        return self.font().bold()

    @property
    def shadow_enabled(self) -> bool:
        return self.graphicsEffect() is not None

    def mouseDoubleClickEvent(self, event):
        self.start_editing()
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged and not value:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        return super().itemChange(change, value)


class FrameItem(QGraphicsPathItem):
    def __init__(
        self,
        rect: QRectF,
        color=QColor("#e53935"),
        width: float = 4,
        rounded: bool = False,
        shadow: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._rect = rect
        self._color = color
        self._width = width
        self._rounded = rounded
        self.setBrush(Qt.BrushStyle.NoBrush)
        self.set_shadow(shadow)
        self._update_path()

    def set_rect(self, rect: QRectF):
        self._rect = rect
        self._update_path()

    def set_color(self, color: QColor):
        self._color = color
        self._update_path()

    def set_width(self, width: float):
        self._width = width
        self._update_path()

    def set_rounded(self, enabled: bool):
        self._rounded = enabled
        self._update_path()

    def set_shadow(self, enabled: bool):
        if enabled:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(16)
            effect.setOffset(3, 5)
            effect.setColor(QColor(0, 0, 0, 130))
            self.setGraphicsEffect(effect)
        else:
            self.setGraphicsEffect(None)

    def _update_path(self):
        path = QPainterPath()
        if self._rounded:
            radius = min(self._rect.width(), self._rect.height()) * 0.12
            path.addRoundedRect(self._rect, radius, radius)
        else:
            path.addRect(self._rect)
        self.setPath(path)
        self.setPen(QPen(self._color, self._width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

    @property
    def color(self) -> QColor:
        return self._color

    @property
    def width(self) -> float:
        return self._width

    @property
    def rounded(self) -> bool:
        return self._rounded

    @property
    def shadow_enabled(self) -> bool:
        return self.graphicsEffect() is not None


_STICKER_GLYPHS = {
    StickerKind.EXCLAMATION: "!",
    StickerKind.QUESTION: "?",
    StickerKind.CHECK: "✓",
    StickerKind.CROSS: "✗",
    StickerKind.STAR: "★",
}


class StickerItem(QGraphicsItem):
    def __init__(
        self,
        kind: StickerKind = StickerKind.EXCLAMATION,
        color=QColor("#e53935"),
        size: float = 48,
        shadow: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._kind = kind
        self._color = color
        self._size = size
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.set_shadow(shadow)

    def set_kind(self, kind: StickerKind):
        self.prepareGeometryChange()
        self._kind = kind
        self.update()

    def set_color(self, color: QColor):
        self._color = color
        self.update()

    def set_size(self, size: float):
        self.prepareGeometryChange()
        self._size = size
        self.update()

    def set_shadow(self, enabled: bool):
        if enabled:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(14)
            effect.setOffset(2, 4)
            effect.setColor(QColor(0, 0, 0, 130))
            self.setGraphicsEffect(effect)
        else:
            self.setGraphicsEffect(None)

    def boundingRect(self) -> QRectF:
        half = self._size / 2
        return QRectF(-half, -half, self._size, self._size)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.boundingRect()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._color))

        font = QFont()
        font.setBold(True)
        font.setPixelSize(int(self._size * 0.5))
        painter.setFont(font)

        if self._kind == StickerKind.WARNING:
            top = QPointF(0, rect.top())
            bottom_left = QPointF(rect.left(), rect.bottom())
            bottom_right = QPointF(rect.right(), rect.bottom())
            triangle_pen = QPen(self._color, self._size * 0.06)
            triangle_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            triangle_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(triangle_pen)
            painter.drawPolygon(QPolygonF([top, bottom_right, bottom_left]))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(rect.adjusted(0, rect.height() * 0.22, 0, 0), Qt.AlignmentFlag.AlignCenter, "!")
        else:
            painter.drawEllipse(rect)
            painter.setPen(QColor("#ffffff"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, _STICKER_GLYPHS[self._kind])

    @property
    def kind(self) -> StickerKind:
        return self._kind

    @property
    def color(self) -> QColor:
        return self._color

    @property
    def size(self) -> float:
        return self._size

    @property
    def shadow_enabled(self) -> bool:
        return self.graphicsEffect() is not None
