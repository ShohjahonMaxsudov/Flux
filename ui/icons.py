from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor
from PySide6.QtWidgets import QWidget


class IconGlyph(QWidget):

    # Hand-drawn vector icons, used instead of emoji everywhere in the
    # app. Several of the pictographic emoji used before (🔥 🌙 🌸 ⭐ 🔒
    # etc.) live outside the Basic Multilingual Plane and need a
    # dedicated color-emoji font to render at all — something a
    # bundled PyInstaller build on Windows doesn't always pick up
    # reliably, so those glyphs were falling back to a generic
    # missing-glyph box that read as a stray checkmark. A vector path
    # drawn with QPainter renders identically regardless of what fonts
    # are installed.

    def __init__(self, name, size=20, color="#FFFFFF", stroke_width=1.8, parent=None):

        super().__init__(parent)

        self.name = name

        self._color = QColor(color)

        self._stroke_width = stroke_width

        self.setFixedSize(size, size)


    def setColor(self, color):

        self._color = QColor(color)

        self.update()


    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()

        h = self.height()

        pen = QPen(self._color)

        pen.setWidthF(self._stroke_width)

        pen.setCapStyle(Qt.RoundCap)

        pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(pen)

        painter.setBrush(Qt.NoBrush)

        draw = _ICONS.get(self.name)

        if draw:

            draw(painter, w, h, self._color)


def _home(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.12, h * 0.5)

    path.lineTo(w * 0.5, h * 0.16)

    path.lineTo(w * 0.88, h * 0.5)

    p.drawPath(path)

    p.drawLine(QPointF(w * 0.22, h * 0.42), QPointF(w * 0.22, h * 0.86))

    p.drawLine(QPointF(w * 0.78, h * 0.42), QPointF(w * 0.78, h * 0.86))

    p.drawLine(QPointF(w * 0.22, h * 0.86), QPointF(w * 0.78, h * 0.86))

    p.drawLine(QPointF(w * 0.42, h * 0.86), QPointF(w * 0.42, h * 0.62))

    p.drawLine(QPointF(w * 0.58, h * 0.86), QPointF(w * 0.58, h * 0.62))

    p.drawLine(QPointF(w * 0.42, h * 0.62), QPointF(w * 0.58, h * 0.62))


def _tasks(p, w, h, color):

    for y in (0.28, 0.5, 0.72):

        p.setBrush(color)

        p.drawEllipse(QPointF(w * 0.18, h * y), w * 0.045, w * 0.045)

        p.setBrush(Qt.NoBrush)

        p.drawLine(QPointF(w * 0.32, h * y), QPointF(w * 0.86, h * y))


def _calendar(p, w, h, color):

    p.drawRoundedRect(QRectF(w * 0.14, h * 0.22, w * 0.72, h * 0.64), 3, 3)

    p.drawLine(QPointF(w * 0.14, h * 0.4), QPointF(w * 0.86, h * 0.4))

    p.drawLine(QPointF(w * 0.32, h * 0.14), QPointF(w * 0.32, h * 0.28))

    p.drawLine(QPointF(w * 0.68, h * 0.14), QPointF(w * 0.68, h * 0.28))


def _chart(p, w, h, color):

    p.drawLine(QPointF(w * 0.16, h * 0.86), QPointF(w * 0.86, h * 0.86))

    p.setBrush(color)

    p.setPen(Qt.NoPen)

    bars = [(0.22, 0.52, 0.16), (0.44, 0.32, 0.16), (0.66, 0.6, 0.16)]

    for x, top, width in bars:

        p.drawRoundedRect(
            QRectF(w * x, h * top, w * width, h * (0.86 - top)),
            2, 2
        )


def _gear(p, w, h, color):

    import math

    center = QPointF(w * 0.5, h * 0.5)

    outer = w * 0.36

    inner = w * 0.24

    p.setBrush(color)

    p.setPen(Qt.NoPen)

    path = QPainterPath()

    teeth = 8

    for i in range(teeth * 2):

        angle = i * math.pi / teeth

        r = outer if i % 2 == 0 else outer * 0.78

        x = center.x() + math.cos(angle) * r

        y = center.y() + math.sin(angle) * r

        if i == 0:

            path.moveTo(x, y)

        else:

            path.lineTo(x, y)

    path.closeSubpath()

    hole = QPainterPath()

    hole.addEllipse(center, w * 0.16, w * 0.16)

    p.drawPath(path.subtracted(hole))


def _check(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.2, h * 0.52)

    path.lineTo(w * 0.42, h * 0.74)

    path.lineTo(w * 0.82, h * 0.28)

    p.drawPath(path)


def _clock(p, w, h, color):

    center = QPointF(w * 0.5, h * 0.5)

    p.drawEllipse(center, w * 0.36, w * 0.36)

    p.drawLine(center, QPointF(w * 0.5, h * 0.28))

    p.drawLine(center, QPointF(w * 0.66, h * 0.58))


def _flame(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.5, h * 0.12)

    path.cubicTo(w * 0.78, h * 0.38, w * 0.7, h * 0.55, w * 0.62, h * 0.42)

    path.cubicTo(w * 0.68, h * 0.65, w * 0.55, h * 0.9, w * 0.4, h * 0.88)

    path.cubicTo(w * 0.2, h * 0.85, w * 0.16, h * 0.62, w * 0.28, h * 0.46)

    path.cubicTo(w * 0.3, h * 0.58, w * 0.4, h * 0.58, w * 0.38, h * 0.44)

    path.cubicTo(w * 0.36, h * 0.28, w * 0.42, h * 0.18, w * 0.5, h * 0.12)

    p.setBrush(color)

    p.drawPath(path)


def _star(p, w, h, color):

    cx, cy = w * 0.5, h * 0.5

    outer = w * 0.42

    inner = w * 0.18

    path = QPainterPath()

    import math

    for i in range(10):

        angle = math.pi / 2 + i * math.pi / 5

        r = outer if i % 2 == 0 else inner

        x = cx - r * math.cos(angle)

        y = cy - r * math.sin(angle)

        if i == 0:

            path.moveTo(x, y)

        else:

            path.lineTo(x, y)

    path.closeSubpath()

    p.setBrush(color)

    p.drawPath(path)


def _moon(p, w, h, color):

    p.setBrush(color)

    full = QPainterPath()

    full.addEllipse(QRectF(w * 0.18, h * 0.18, w * 0.64, h * 0.64))

    cut = QPainterPath()

    cut.addEllipse(QRectF(w * 0.32, h * 0.1, w * 0.64, h * 0.64))

    p.drawPath(full.subtracted(cut))


def _sun(p, w, h, color):

    center = QPointF(w * 0.5, h * 0.5)

    p.setBrush(color)

    p.drawEllipse(center, w * 0.2, w * 0.2)

    p.setBrush(Qt.NoBrush)

    import math

    for i in range(8):

        angle = i * math.pi / 4

        x1 = center.x() + math.cos(angle) * w * 0.3

        y1 = center.y() + math.sin(angle) * w * 0.3

        x2 = center.x() + math.cos(angle) * w * 0.42

        y2 = center.y() + math.sin(angle) * w * 0.42

        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def _blossom(p, w, h, color):

    cx, cy = w * 0.5, h * 0.5

    p.setPen(Qt.NoPen)

    p.setBrush(color)

    import math

    petal_r = w * 0.15

    orbit = w * 0.26

    for i in range(5):

        angle = i * (2 * math.pi / 5) - math.pi / 2

        px = cx + math.cos(angle) * orbit

        py = cy + math.sin(angle) * orbit

        p.drawEllipse(QPointF(px, py), petal_r, petal_r)

    p.setBrush(QColor(255, 255, 255, 235))

    p.drawEllipse(QPointF(cx, cy), w * 0.11, w * 0.11)


def _lock(p, w, h, color):

    body = QRectF(w * 0.24, h * 0.46, w * 0.52, h * 0.42)

    p.drawRoundedRect(body, 3, 3)

    shackle = QRectF(w * 0.32, h * 0.16, w * 0.36, h * 0.4)

    p.drawArc(shackle, 0, 180 * 16)

    p.drawLine(QPointF(w * 0.32, h * 0.36), QPointF(w * 0.32, h * 0.46))

    p.drawLine(QPointF(w * 0.68, h * 0.36), QPointF(w * 0.68, h * 0.46))


def _plus(p, w, h, color):

    p.drawLine(QPointF(w * 0.5, h * 0.2), QPointF(w * 0.5, h * 0.8))

    p.drawLine(QPointF(w * 0.2, h * 0.5), QPointF(w * 0.8, h * 0.5))


def _back(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.62, h * 0.2)

    path.lineTo(w * 0.32, h * 0.5)

    path.lineTo(w * 0.62, h * 0.8)

    p.drawPath(path)


def _more(p, w, h, color):

    p.setBrush(color)

    for x in (0.3, 0.5, 0.7):

        p.drawEllipse(QPointF(w * x, h * 0.5), w * 0.055, w * 0.055)


def _share(p, w, h, color):

    p.drawLine(QPointF(w * 0.5, h * 0.16), QPointF(w * 0.5, h * 0.52))

    path = QPainterPath()

    path.moveTo(w * 0.34, h * 0.32)

    path.lineTo(w * 0.5, h * 0.16)

    path.lineTo(w * 0.66, h * 0.32)

    p.drawPath(path)

    p.drawRoundedRect(QRectF(w * 0.22, h * 0.6, w * 0.56, h * 0.26), 4, 4)


def _attachment(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.66, h * 0.24)

    path.lineTo(w * 0.36, h * 0.54)

    path.arcTo(QRectF(w * 0.28, h * 0.46, w * 0.24, h * 0.24), 90, 270)

    path.lineTo(w * 0.62, h * 0.36)

    p.drawPath(path)


def _sparkle(p, w, h, color):

    p.setBrush(color)

    path = QPainterPath()

    path.moveTo(w * 0.5, h * 0.12)

    path.lineTo(w * 0.58, h * 0.42)

    path.lineTo(w * 0.88, h * 0.5)

    path.lineTo(w * 0.58, h * 0.58)

    path.lineTo(w * 0.5, h * 0.88)

    path.lineTo(w * 0.42, h * 0.58)

    path.lineTo(w * 0.12, h * 0.5)

    path.lineTo(w * 0.42, h * 0.42)

    path.closeSubpath()

    p.drawPath(path)


def _notebook(p, w, h, color):

    p.drawRoundedRect(QRectF(w * 0.2, h * 0.14, w * 0.6, h * 0.72), 4, 4)

    for y in (0.36, 0.5, 0.64):

        p.drawLine(QPointF(w * 0.32, h * y), QPointF(w * 0.68, h * y))

    p.drawLine(QPointF(w * 0.2, h * 0.28), QPointF(w * 0.32, h * 0.28))


_ICONS = {

    "home": _home,

    "tasks": _tasks,

    "calendar": _calendar,

    "chart": _chart,

    "gear": _gear,

    "check": _check,

    "clock": _clock,

    "flame": _flame,

    "star": _star,

    "moon": _moon,

    "sun": _sun,

    "blossom": _blossom,

    "lock": _lock,

    "plus": _plus,

    "back": _back,

    "more": _more,

    "share": _share,

    "attachment": _attachment,

    "sparkle": _sparkle,

    "notebook": _notebook,

}
