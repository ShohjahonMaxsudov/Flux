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


def _void(p, w, h, color):

    # An eclipse: thin ring around a solid core.

    center = QPointF(w * 0.5, h * 0.5)

    p.drawEllipse(center, w * 0.36, w * 0.36)

    p.setBrush(color)

    p.drawEllipse(center, w * 0.13, w * 0.13)

def _wave(p, w, h, color):

    # Two stacked swells.

    for y in (0.40, 0.66):

        path = QPainterPath()

        path.moveTo(w * 0.12, h * y)

        path.cubicTo(
            w * 0.26, h * (y - 0.16),
            w * 0.38, h * (y - 0.16),
            w * 0.5, h * y
        )

        path.cubicTo(
            w * 0.62, h * (y + 0.16),
            w * 0.74, h * (y + 0.16),
            w * 0.88, h * y
        )

        p.drawPath(path)

def _arrow_right(p, w, h, color):

    p.drawLine(QPointF(w * 0.2, h * 0.5), QPointF(w * 0.8, h * 0.5))

    path = QPainterPath()

    path.moveTo(w * 0.56, h * 0.26)

    path.lineTo(w * 0.8, h * 0.5)

    path.lineTo(w * 0.56, h * 0.74)

    p.drawPath(path)

def _planet(p, w, h, color):

    # A ringed planet.

    center = QPointF(w * 0.5, h * 0.5)

    p.drawEllipse(center, w * 0.22, w * 0.22)

    p.save()

    p.translate(center)

    p.rotate(-22)

    p.drawEllipse(QPointF(0, 0), w * 0.44, w * 0.13)

    p.restore()

def _aurora(p, w, h, color):

    # An arch of light with falling rays.

    arch = QPainterPath()

    arch.moveTo(w * 0.1, h * 0.62)

    arch.cubicTo(w * 0.25, h * 0.14, w * 0.75, h * 0.14, w * 0.9, h * 0.62)

    p.drawPath(arch)

    for x, top in ((0.3, 0.36), (0.5, 0.26), (0.7, 0.36)):

        p.drawLine(QPointF(w * x, h * top), QPointF(w * x, h * 0.86))

def _sunset(p, w, h, color):

    p.drawArc(QRectF(w * 0.22, h * 0.26, w * 0.56, h * 0.56), 0, 180 * 16)

    p.drawLine(QPointF(w * 0.1, h * 0.54), QPointF(w * 0.9, h * 0.54))

    p.drawLine(QPointF(w * 0.24, h * 0.68), QPointF(w * 0.76, h * 0.68))

    p.drawLine(QPointF(w * 0.36, h * 0.82), QPointF(w * 0.64, h * 0.82))

def _tree(p, w, h, color):

    for top, half, bottom in ((0.12, 0.2, 0.44), (0.28, 0.28, 0.66), (0.44, 0.36, 0.86)):

        path = QPainterPath()

        path.moveTo(w * 0.5, h * top)

        path.lineTo(w * (0.5 - half), h * bottom)

        path.lineTo(w * (0.5 + half), h * bottom)

        path.closeSubpath()

        p.drawPath(path)

def _snowflake(p, w, h, color):

    import math

    center = QPointF(w * 0.5, h * 0.5)

    for i in range(3):

        angle = i * math.pi / 3 + math.pi / 2

        dx = math.cos(angle) * w * 0.38

        dy = math.sin(angle) * w * 0.38

        p.drawLine(QPointF(center.x() - dx, center.y() - dy), QPointF(center.x() + dx, center.y() + dy))

def _contrast(p, w, h, color):

    # A circle, right half filled.

    center = QPointF(w * 0.5, h * 0.5)

    p.drawEllipse(center, w * 0.36, w * 0.36)

    p.setBrush(color)

    path = QPainterPath()

    path.moveTo(w * 0.5, h * 0.14)

    path.arcTo(QRectF(w * 0.14, h * 0.14, w * 0.72, h * 0.72), 90, -180)

    path.closeSubpath()

    p.drawPath(path)

def _timer(p, w, h, color):

    # A stopwatch: ring, a small crown button on top, a hand pointing
    # to about 20 minutes past.

    center = QPointF(w * 0.5, h * 0.56)

    p.drawEllipse(center, w * 0.34, w * 0.34)

    p.drawLine(QPointF(w * 0.5, h * 0.17), QPointF(w * 0.5, h * 0.09))

    p.drawLine(QPointF(w * 0.40, h * 0.09), QPointF(w * 0.60, h * 0.09))

    p.drawLine(center, QPointF(w * 0.66, h * 0.42))


def _sort(p, w, h, color):

    # Two arrows, one up one down — the universal "ascending/descending"
    # affordance.

    p.drawLine(QPointF(w * 0.32, h * 0.78), QPointF(w * 0.32, h * 0.22))

    top = QPainterPath()

    top.moveTo(w * 0.20, h * 0.36)

    top.lineTo(w * 0.32, h * 0.22)

    top.lineTo(w * 0.44, h * 0.36)

    p.drawPath(top)

    p.drawLine(QPointF(w * 0.68, h * 0.22), QPointF(w * 0.68, h * 0.78))

    bottom = QPainterPath()

    bottom.moveTo(w * 0.56, h * 0.64)

    bottom.lineTo(w * 0.68, h * 0.78)

    bottom.lineTo(w * 0.80, h * 0.64)

    p.drawPath(bottom)


def _undo(p, w, h, color):

    # A curved arrow sweeping back to the left.

    path = QPainterPath()

    path.moveTo(w * 0.78, h * 0.66)

    path.cubicTo(w * 0.78, h * 0.30, w * 0.30, h * 0.20, w * 0.24, h * 0.42)

    p.drawPath(path)

    head = QPainterPath()

    head.moveTo(w * 0.34, h * 0.26)

    head.lineTo(w * 0.22, h * 0.42)

    head.lineTo(w * 0.40, h * 0.50)

    p.drawPath(head)


def _palette(p, w, h, color):

    # A painter's palette with a thumb-hole and a few colour dabs.

    path = QPainterPath()

    path.moveTo(w * 0.5, h * 0.14)

    path.cubicTo(w * 0.86, h * 0.14, w * 0.90, h * 0.60, w * 0.62, h * 0.62)

    path.cubicTo(w * 0.50, h * 0.63, w * 0.52, h * 0.78, w * 0.38, h * 0.80)

    path.cubicTo(w * 0.14, h * 0.82, w * 0.14, h * 0.14, w * 0.5, h * 0.14)

    p.drawPath(path)

    p.setBrush(color)

    for cx, cy, r in (
        (0.37, 0.32, 0.045),
        (0.52, 0.28, 0.045),
        (0.66, 0.36, 0.045),
    ):

        p.drawEllipse(QPointF(w * cx, h * cy), w * r, w * r)

    p.setBrush(Qt.NoBrush)


def _play(p, w, h, color):

    p.setBrush(color)

    path = QPainterPath()

    path.moveTo(w * 0.32, h * 0.20)

    path.lineTo(w * 0.32, h * 0.80)

    path.lineTo(w * 0.80, h * 0.5)

    path.closeSubpath()

    p.drawPath(path)

    p.setBrush(Qt.NoBrush)


def _pause(p, w, h, color):

    p.setBrush(color)

    p.drawRoundedRect(QRectF(w * 0.28, h * 0.20, w * 0.16, h * 0.60), 2, 2)

    p.drawRoundedRect(QRectF(w * 0.56, h * 0.20, w * 0.16, h * 0.60), 2, 2)

    p.setBrush(Qt.NoBrush)


def _reset(p, w, h, color):

    # A ring with a gap, closed by an arrowhead — "start over".

    rect = QRectF(w * 0.18, h * 0.18, w * 0.64, h * 0.64)

    p.drawArc(rect, 40 * 16, 260 * 16)

    head = QPainterPath()

    head.moveTo(w * 0.66, h * 0.16)

    head.lineTo(w * 0.80, h * 0.24)

    head.lineTo(w * 0.68, h * 0.36)

    p.drawPath(head)


def _close(p, w, h, color):

    p.drawLine(QPointF(w * 0.26, h * 0.26), QPointF(w * 0.74, h * 0.74))

    p.drawLine(QPointF(w * 0.74, h * 0.26), QPointF(w * 0.26, h * 0.74))


def _bell(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.28, h * 0.62)

    path.lineTo(w * 0.28, h * 0.40)

    path.cubicTo(w * 0.28, h * 0.20, w * 0.72, h * 0.20, w * 0.72, h * 0.40)

    path.lineTo(w * 0.72, h * 0.62)

    path.lineTo(w * 0.80, h * 0.72)

    path.lineTo(w * 0.20, h * 0.72)

    path.closeSubpath()

    p.drawPath(path)

    p.drawLine(QPointF(w * 0.44, h * 0.80), QPointF(w * 0.56, h * 0.80))


def _alert(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.5, h * 0.16)

    path.lineTo(w * 0.86, h * 0.80)

    path.lineTo(w * 0.14, h * 0.80)

    path.closeSubpath()

    p.drawPath(path)

    p.drawLine(QPointF(w * 0.5, h * 0.40), QPointF(w * 0.5, h * 0.60))

    p.setBrush(color)

    p.drawEllipse(QPointF(w * 0.5, h * 0.70), w * 0.025, w * 0.025)

    p.setBrush(Qt.NoBrush)




def _chevron_down(p, w, h, color):

    path = QPainterPath()

    path.moveTo(w * 0.22, h * 0.36)

    path.lineTo(w * 0.5, h * 0.64)

    path.lineTo(w * 0.78, h * 0.36)

    p.drawPath(path)


def _filter(p, w, h, color):

    p.drawLine(QPointF(w * 0.16, h * 0.28), QPointF(w * 0.84, h * 0.28))

    p.drawLine(QPointF(w * 0.16, h * 0.50), QPointF(w * 0.84, h * 0.50))

    p.drawLine(QPointF(w * 0.16, h * 0.72), QPointF(w * 0.84, h * 0.72))

    p.setBrush(color)

    p.drawEllipse(QPointF(w * 0.36, h * 0.28), w * 0.06, w * 0.06)

    p.drawEllipse(QPointF(w * 0.64, h * 0.50), w * 0.06, w * 0.06)

    p.drawEllipse(QPointF(w * 0.44, h * 0.72), w * 0.06, w * 0.06)

    p.setBrush(Qt.NoBrush)


def _search(p, w, h, color):

    center = QPointF(w * 0.43, h * 0.43)

    p.drawEllipse(center, w * 0.25, w * 0.25)

    p.drawLine(
        QPointF(w * 0.61, h * 0.61),
        QPointF(w * 0.83, h * 0.83)
    )


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

    "void": _void,

    "wave": _wave,

    "arrow_right": _arrow_right,

    "planet": _planet,

    "aurora": _aurora,

    "sunset": _sunset,

    "tree": _tree,

    "snowflake": _snowflake,

    "contrast": _contrast,

    "timer": _timer,

    "sort": _sort,

    "undo": _undo,

    "palette": _palette,

    "play": _play,

    "pause": _pause,

    "reset": _reset,

    "close": _close,

    "bell": _bell,

    "alert": _alert,

    "chevron_down": _chevron_down,

    "filter": _filter,

    "search": _search,

}
