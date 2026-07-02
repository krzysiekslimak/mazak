import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen, QPixmap, QPolygonF

from .tools import ArrowStyle, BubbleShape, StickerKind

_STROKE = QColor("#3c4043")
_ACCENT = QColor("#2f6fed")


def _new_pixmap(size=32):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    return pm


def _painter(pm):
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(_STROKE, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.setBrush(Qt.BrushStyle.NoBrush)
    return p


def select_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.setBrush(QBrush(_STROKE))
    pointer = QPolygonF(
        [
            QPointF(8, 5),
            QPointF(8, 25),
            QPointF(13, 20.5),
            QPointF(16.5, 27),
            QPointF(19.5, 25.5),
            QPointF(16, 19),
            QPointF(23, 18.5),
        ]
    )
    p.drawPolygon(pointer)
    p.end()
    return QIcon(pm)


def arrow_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    start = QPointF(6, 26)
    end = QPointF(25, 7)
    p.drawLine(start, end)
    angle = math.atan2(end.y() - start.y(), end.x() - start.x())
    head = 8
    p1 = QPointF(end.x() - math.cos(angle - math.pi / 7) * head, end.y() - math.sin(angle - math.pi / 7) * head)
    p2 = QPointF(end.x() - math.cos(angle + math.pi / 7) * head, end.y() - math.sin(angle + math.pi / 7) * head)
    p.setBrush(QBrush(_STROKE))
    p.drawPolygon(QPolygonF([end, p1, p2]))
    p.end()
    return QIcon(pm)


def bubble_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    rect = QRectF(5, 5, 22, 15)
    p.drawRoundedRect(rect, 4, 4)
    p.setBrush(QBrush(_STROKE))
    tail = QPolygonF([QPointF(10, 20), QPointF(9, 27), QPointF(15, 20.3)])
    p.drawPolygon(tail)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawLine(QPointF(9, 10.5), QPointF(23, 10.5))
    p.drawLine(QPointF(9, 15), QPointF(19, 15))
    p.end()
    return QIcon(pm)


def bubble_shape_icon(shape: BubbleShape, size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)

    if shape == BubbleShape.OVAL:
        rect = QRectF(4, 6, 24, 15)
        p.drawEllipse(rect)
        p.setBrush(QBrush(_STROKE))
        tail = QPolygonF([QPointF(12, 19.5), QPointF(9.5, 27), QPointF(17, 20.5)])
        p.drawPolygon(tail)
    elif shape == BubbleShape.CLOUD:
        p.setBrush(Qt.BrushStyle.NoBrush)
        for cx, cy, r in [
            (10, 11, 5.5),
            (16, 7.5, 6.2),
            (22, 11, 5.5),
            (7.5, 15.5, 4.8),
            (24.5, 15.5, 4.8),
            (12, 18.5, 5.2),
            (20, 18.5, 5.2),
        ]:
            p.drawEllipse(QPointF(cx, cy), r, r)
        p.setBrush(QBrush(_STROKE))
        p.drawEllipse(QPointF(10, 24.5), 2.4, 2.4)
        p.drawEllipse(QPointF(7, 28), 1.4, 1.4)
    else:
        rect = QRectF(5, 5, 22, 15)
        p.drawRoundedRect(rect, 4, 4)
        p.setBrush(QBrush(_STROKE))
        tail = QPolygonF([QPointF(10, 20), QPointF(9, 27), QPointF(15, 20.3)])
        p.drawPolygon(tail)

    p.end()
    return QIcon(pm)


def border_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawRoundedRect(QRectF(6, 6, 20, 20), 5, 5)
    p.end()
    return QIcon(pm)


def frame_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawRect(QRectF(5, 6, 22, 20))
    p.end()
    return QIcon(pm)


def corner_style_icon(rounded: bool, size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    rect = QRectF(6, 7, 20, 18)
    if rounded:
        p.drawRoundedRect(rect, 7, 7)
    else:
        p.drawRect(rect)
    p.end()
    return QIcon(pm)


def sticker_icon(kind: StickerKind, size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    rect = QRectF(3, 3, size - 6, size - 6)

    font = QFont()
    font.setBold(True)
    font.setPixelSize(int(size * 0.46))
    p.setFont(font)

    glyphs = {
        StickerKind.EXCLAMATION: "!",
        StickerKind.QUESTION: "?",
        StickerKind.CHECK: "✓",
        StickerKind.CROSS: "✗",
        StickerKind.STAR: "★",
    }

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(_ACCENT))

    if kind == StickerKind.WARNING:
        top = QPointF(size / 2, rect.top())
        bl = QPointF(rect.left(), rect.bottom())
        br = QPointF(rect.right(), rect.bottom())
        p.drawPolygon(QPolygonF([top, br, bl]))
        p.setPen(QColor("#ffffff"))
        p.drawText(rect.adjusted(0, rect.height() * 0.22, 0, 0), Qt.AlignmentFlag.AlignCenter, "!")
    else:
        p.drawEllipse(rect)
        p.setPen(QColor("#ffffff"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, glyphs[kind])

    p.end()
    return QIcon(pm)


def bold_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = QFont()
    font.setBold(True)
    font.setPointSize(17)
    p.setFont(font)
    p.setPen(QPen(_STROKE))
    p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "B")
    p.end()
    return QIcon(pm)


def text_shadow_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = QFont()
    font.setBold(True)
    font.setPointSize(16)
    p.setFont(font)
    p.setPen(QPen(QColor(0, 0, 0, 110)))
    p.drawText(QRectF(2.5, 2.5, size, size), Qt.AlignmentFlag.AlignCenter, "A")
    p.setPen(QPen(_STROKE))
    p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "A")
    p.end()
    return QIcon(pm)


def text_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    font = QFont()
    font.setBold(True)
    font.setPointSize(16)
    p.setFont(font)
    p.setPen(QPen(_STROKE))
    p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "T")
    p.end()
    return QIcon(pm)


def _magnifier_icon(size=32, symbol: str | None = None) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    circle = QRectF(4, 4, 16, 16)
    p.drawEllipse(circle)
    p.drawLine(QPointF(16.5, 16.5), QPointF(24, 24))
    if symbol:
        pen = QPen(_STROKE, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        cx, cy = circle.center().x(), circle.center().y()
        p.drawLine(QPointF(cx - 4, cy), QPointF(cx + 4, cy))
        if symbol == "+":
            p.drawLine(QPointF(cx, cy - 4), QPointF(cx, cy + 4))
    p.end()
    return QIcon(pm)


def zoom_in_icon(size=32) -> QIcon:
    return _magnifier_icon(size, "+")


def zoom_out_icon(size=32) -> QIcon:
    return _magnifier_icon(size, "-")


def zoom_fit_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawRect(QRectF(6, 7, 20, 18))
    arrow_pen = QPen(_STROKE, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(arrow_pen)
    p.drawLine(QPointF(11, 12), QPointF(11, 16))
    p.drawLine(QPointF(11, 12), QPointF(15, 12))
    p.drawLine(QPointF(21, 20), QPointF(21, 16))
    p.drawLine(QPointF(21, 20), QPointF(17, 20))
    p.end()
    return QIcon(pm)


def open_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawRoundedRect(QRectF(5, 11, 22, 14), 2, 2)
    p.drawLine(QPointF(5, 11), QPointF(9, 7))
    p.drawLine(QPointF(9, 7), QPointF(16, 7))
    p.drawLine(QPointF(16, 7), QPointF(19, 11))
    p.end()
    return QIcon(pm)


def export_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawLine(QPointF(16, 5), QPointF(16, 18))
    p.setBrush(QBrush(_STROKE))
    p.drawPolygon(QPolygonF([QPointF(10, 13), QPointF(22, 13), QPointF(16, 21)]))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawLine(QPointF(6, 24), QPointF(6, 27))
    p.drawLine(QPointF(6, 27), QPointF(26, 27))
    p.drawLine(QPointF(26, 27), QPointF(26, 24))
    p.end()
    return QIcon(pm)


def delete_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawLine(QPointF(8, 9), QPointF(24, 9))
    p.drawLine(QPointF(12, 9), QPointF(13, 6))
    p.drawLine(QPointF(13, 6), QPointF(19, 6))
    p.drawLine(QPointF(19, 6), QPointF(20, 9))
    p.drawRoundedRect(QRectF(9, 9, 14, 17), 2, 2)
    p.drawLine(QPointF(13, 13), QPointF(13, 22))
    p.drawLine(QPointF(16, 13), QPointF(16, 22))
    p.drawLine(QPointF(19, 13), QPointF(19, 22))
    p.end()
    return QIcon(pm)


def undo_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    rect = QRectF(6, 6, 20, 20)
    p.drawArc(rect, 20 * 16, 280 * 16)

    cx, cy, r = 16.0, 16.0, 10.0
    ang = math.radians(20)
    ex = cx + r * math.cos(ang)
    ey = cy + r * math.sin(ang)
    tangent = ang - math.pi / 2
    p1 = QPointF(ex + 7 * math.cos(tangent + 2.6), ey + 7 * math.sin(tangent + 2.6))
    p2 = QPointF(ex + 7 * math.cos(tangent - 2.6), ey + 7 * math.sin(tangent - 2.6))
    p.setBrush(QBrush(_STROKE))
    p.drawPolygon(QPolygonF([QPointF(ex, ey), p1, p2]))
    p.end()
    return QIcon(pm)


def redo_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.translate(size, 0)
    p.scale(-1, 1)
    rect = QRectF(6, 6, 20, 20)
    p.drawArc(rect, 20 * 16, 280 * 16)

    cx, cy, r = 16.0, 16.0, 10.0
    ang = math.radians(20)
    ex = cx + r * math.cos(ang)
    ey = cy + r * math.sin(ang)
    tangent = ang - math.pi / 2
    p1 = QPointF(ex + 7 * math.cos(tangent + 2.6), ey + 7 * math.sin(tangent + 2.6))
    p2 = QPointF(ex + 7 * math.cos(tangent - 2.6), ey + 7 * math.sin(tangent - 2.6))
    p.setBrush(QBrush(_STROKE))
    p.drawPolygon(QPolygonF([QPointF(ex, ey), p1, p2]))
    p.end()
    return QIcon(pm)


def blur_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    rect = QRectF(5, 5, 22, 22)
    cols = 4
    cell = rect.width() / cols
    shades = ["#c3c7cb", "#9aa0a6", "#6b7178", "#3c4043"]
    for row in range(cols):
        for col in range(cols):
            shade = shades[(row * 7 + col * 3) % len(shades)]
            p.setBrush(QBrush(QColor(shade)))
            p.drawRect(QRectF(rect.left() + col * cell, rect.top() + row * cell, cell, cell))
    p.end()
    return QIcon(pm)


def crop_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawLine(QPointF(10, 4), QPointF(10, 24))
    p.drawLine(QPointF(10, 24), QPointF(28, 24))
    p.drawLine(QPointF(22, 28), QPointF(22, 8))
    p.drawLine(QPointF(22, 8), QPointF(4, 8))
    p.end()
    return QIcon(pm)


def paste_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawRoundedRect(QRectF(7, 7, 18, 20), 2, 2)
    p.drawRoundedRect(QRectF(12, 4, 8, 5), 1.5, 1.5)
    p.drawLine(QPointF(16, 14), QPointF(16, 22))
    p.drawLine(QPointF(12, 18), QPointF(20, 18))
    p.end()
    return QIcon(pm)


def copy_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = _painter(pm)
    p.drawRoundedRect(QRectF(11, 5, 15, 18), 2, 2)
    p.drawRoundedRect(QRectF(6, 10, 15, 18), 2, 2)
    p.end()
    return QIcon(pm)


def thickness_icon(px_width: float, size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(_STROKE, px_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    y = size / 2
    p.drawLine(QPointF(7, y), QPointF(size - 7, y))
    p.end()
    return QIcon(pm)


def arrow_style_icon(style: ArrowStyle, color=_STROKE, size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    start = QPointF(6, size - 7)
    end = QPointF(size - 6, 7)
    angle = math.atan2(end.y() - start.y(), end.x() - start.x())

    if style == ArrowStyle.SLIM:
        p.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        head = 7
        spread = math.pi / 6
        p.drawLine(start, end)
        p1 = QPointF(end.x() - math.cos(angle - spread) * head, end.y() - math.sin(angle - spread) * head)
        p2 = QPointF(end.x() - math.cos(angle + spread) * head, end.y() - math.sin(angle + spread) * head)
        p.drawLine(p1, end)
        p.drawLine(end, p2)
    elif style == ArrowStyle.BOLD:
        p.setPen(QPen(color, 4.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(QBrush(color))
        head = 10
        spread = math.pi / 5.5
        back = QPointF(end.x() - math.cos(angle) * head * 0.5, end.y() - math.sin(angle) * head * 0.5)
        p.drawLine(start, back)
        p1 = QPointF(end.x() - math.cos(angle - spread) * head, end.y() - math.sin(angle - spread) * head)
        p2 = QPointF(end.x() - math.cos(angle + spread) * head, end.y() - math.sin(angle + spread) * head)
        p.drawPolygon(QPolygonF([end, p1, p2]))
    else:
        p.setPen(QPen(color, 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(QBrush(color))
        head = 8
        spread = math.pi / 7
        back = QPointF(end.x() - math.cos(angle) * head * 0.6, end.y() - math.sin(angle) * head * 0.6)
        p.drawLine(start, back)
        p1 = QPointF(end.x() - math.cos(angle - spread) * head, end.y() - math.sin(angle - spread) * head)
        p2 = QPointF(end.x() - math.cos(angle + spread) * head, end.y() - math.sin(angle + spread) * head)
        p.drawPolygon(QPolygonF([end, p1, p2]))

    p.end()
    return QIcon(pm)


def shadow_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(0, 0, 0, 60)))
    p.drawRoundedRect(QRectF(10, 10, 16, 16), 4, 4)
    p.setPen(QPen(_STROKE, 2))
    p.setBrush(QBrush(QColor("#ffffff")))
    p.drawRoundedRect(QRectF(6, 6, 16, 16), 4, 4)
    p.end()
    return QIcon(pm)


def custom_color_icon(size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    segments = [QColor("#e53935"), QColor("#fdd835"), QColor("#43a047"), QColor("#1e88e5"), QColor("#8e24aa")]
    rect = QRectF(4, 4, size - 8, size - 8)
    span = 360 * 16 // len(segments)
    for i, c in enumerate(segments):
        p.setBrush(QBrush(c))
        p.drawPie(rect, i * span, span + 8)
    p.setBrush(QBrush(QColor("#ffffff")))
    inner = size * 0.22
    p.drawEllipse(QRectF(size / 2 - inner, size / 2 - inner, inner * 2, inner * 2))
    p.end()
    return QIcon(pm)


def color_swatch_icon(color: QColor, size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor("#9aa0a6"), 1.4))
    p.setBrush(QBrush(color))
    margin = size * 0.16
    p.drawRoundedRect(QRectF(margin, margin, size - 2 * margin, size - 2 * margin), 6, 6)
    p.end()
    return QIcon(pm)


def circle_swatch_icon(color: QColor, size=32) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(0, 0, 0, 35), 1.2))
    p.setBrush(QBrush(color))
    margin = size * 0.12
    p.drawEllipse(QRectF(margin, margin, size - 2 * margin, size - 2 * margin))
    p.end()
    return QIcon(pm)


def app_icon(size=64) -> QIcon:
    pm = _new_pixmap(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(_ACCENT))
    p.drawRoundedRect(QRectF(2, 2, size - 4, size - 4), size * 0.22, size * 0.22)
    font = QFont()
    font.setBold(True)
    font.setPointSize(int(size * 0.42))
    p.setPen(QColor("#ffffff"))
    p.setFont(font)
    p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "M")
    p.end()
    return QIcon(pm)
