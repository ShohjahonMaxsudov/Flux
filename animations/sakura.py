import random
import math

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QPainterPath,
    QLinearGradient,
    QRadialGradient,
    QPixmap,
)
from PySide6.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsBlurEffect,
)


def _blurred(pixmap, radius):

    # Bakes a real blur into a copy of `pixmap` via a throwaway
    # QGraphicsScene, rather than re-blurring every paint. Called only
    # when the atmosphere layer is (re)built — once at startup and once
    # per resize — never from the per-frame paintEvent.

    if radius <= 0 or pixmap.isNull():
        return pixmap

    scene = QGraphicsScene()

    item = QGraphicsPixmapItem(pixmap)

    effect = QGraphicsBlurEffect()

    effect.setBlurRadius(radius)

    item.setGraphicsEffect(effect)

    scene.addItem(item)

    result = QPixmap(pixmap.size())

    result.fill(Qt.transparent)

    painter = QPainter(result)

    painter.setRenderHint(QPainter.Antialiasing)

    scene.render(
        painter,
        QRectF(0, 0, pixmap.width(), pixmap.height()),
        QRectF(0, 0, pixmap.width(), pixmap.height())
    )

    painter.end()

    return result


class Petal:

    # Two depth layers give the falling petals some parallax: "far"
    # petals are small, slow, dim and more numerous; "near" petals are
    # bigger, faster and fully opaque, like they're closer to camera.

    def __init__(self, width, height):

        self.reset(width, height, first=True)


    def reset(self, width, height, first=False):

        self.near = random.random() < 0.3

        self.x = random.uniform(0, max(width, 1))

        self.y = (
            random.uniform(0, max(height, 1))
            if first
            else random.uniform(-160, -20)
        )

        self.size = (
            random.uniform(9, 15)
            if self.near
            else random.uniform(4, 8)
        )

        self.speed = (
            random.uniform(0.9, 1.6)
            if self.near
            else random.uniform(0.25, 0.55)
        )

        self.drift = (
            random.uniform(0.35, 0.9)
            if self.near
            else random.uniform(0.1, 0.4)
        )

        self.swing = random.uniform(0, math.pi * 2)

        self.swing_speed = random.uniform(0.015, 0.035)

        self.rotation = random.uniform(0, 360)

        self.rotation_speed = random.uniform(-1.4, 1.4)

        self.opacity = (
            random.uniform(0.6, 0.9)
            if self.near
            else random.uniform(0.18, 0.42)
        )

        pick = random.random()

        if pick < 0.5:
            self.color = QColor(240, 120, 165)
        elif pick < 0.85:
            self.color = QColor(255, 150, 185)
        else:
            self.color = QColor(255, 190, 210)


    def update(self, width, height, step=1.0):

        self.y += self.speed * step

        self.swing += self.swing_speed * step

        self.x += math.sin(self.swing) * self.drift * step

        self.rotation += self.rotation_speed * step

        if self.y > height + 40 or self.x < -60 or self.x > width + 60:

            self.reset(width, height)


class SakuraBackground(QWidget):

    FRAME_MS = 16

    # Atmospheric Sakura background: a dusk-pink gradient sky, a warm
    # off-center glow, two blurred cherry-blossom branch silhouettes at
    # different depths (baked once per resize, not per frame), and
    # falling petals with a near/far split for a sense of depth.
    #
    # Deliberately NOT "dark mode + pink": the branches, glow and
    # multi-depth petals are what create the atmosphere; the glass UI
    # sitting on top of this can stay comparatively restrained.

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.petals = []

        self._initialized = False

        self._atmosphere = QPixmap()

        self._atmosphere_size = None

        self.timer = QTimer(self)

        self.timer.timeout.connect(self._tick)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)

        self.timer.start(self.FRAME_MS)


    def start(self):

        if not self.timer.isActive():

            self.timer.start(self.FRAME_MS)


    def stop(self):

        self.timer.stop()


    def _init_petals(self):

        if self.width() <= 0 or self.height() <= 0:
            return

        self.petals = [
            Petal(self.width(), self.height())
            for _ in range(70)
        ]

        self._initialized = True


    def resizeEvent(self, event):

        super().resizeEvent(event)

        self._atmosphere_size = None

        if not self._initialized:

            self._init_petals()


    def _tick(self):

        if not self._initialized:

            self._init_petals()

        step = self.FRAME_MS / 30.0

        for petal in self.petals:

            petal.update(self.width(), self.height(), step)

        self.update()


    def _branch_layer(self, w, h, scale, x_offset, flip, alpha):

        # One gnarled branch with a few blossom clusters, on its own
        # transparent pixmap so it can be blurred in isolation from the
        # sky/glow layer beneath it.

        pm = QPixmap(w, h)

        pm.fill(Qt.transparent)

        painter = QPainter(pm)

        painter.setRenderHint(QPainter.Antialiasing)

        direction = -1 if flip else 1

        origin_x = w * (0.94 - x_offset) if flip else w * (0.06 + x_offset)

        x, y = origin_x, -20.0

        pen_width = 24 * scale

        wood = QColor(48, 26, 22, int(255 * alpha))

        pen = QPen(wood, pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        painter.setPen(pen)

        segments = 5

        for i in range(segments):

            progress = (i + 1) / segments

            nx = x + direction * (55 + i * 20) * scale

            ny = h * progress * 0.55

            ctrl_x = x + direction * 38 * scale

            ctrl_y = (y + ny) / 2


            seg = QPainterPath()

            seg.moveTo(x, y)

            seg.quadTo(ctrl_x, ctrl_y, nx, ny)

            painter.drawPath(seg)


            pen_width = max(pen_width * 0.75, 3)

            painter.setPen(
                QPen(wood, pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            )


            if i >= 1:

                twig_len = 34 * scale * (1 - progress * 0.4)

                tx = nx + direction * twig_len * 0.8

                ty = ny - twig_len * 0.7


                twig = QPainterPath()

                twig.moveTo(nx, ny)

                twig.lineTo(tx, ty)

                painter.drawPath(twig)


                painter.setPen(Qt.NoPen)

                painter.setBrush(QColor(255, 190, 210, int(215 * alpha)))

                for _ in range(5):

                    bx = tx + random.uniform(-16, 16) * scale

                    by = ty + random.uniform(-16, 16) * scale

                    bsize = random.uniform(6, 11) * scale

                    painter.drawEllipse(QPointF(bx, by), bsize, bsize)


                painter.setPen(
                    QPen(wood, pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                )


            x, y = nx, ny


        painter.end()

        return pm


    def _build_atmosphere(self):

        w = max(self.width(), 1)

        h = max(self.height(), 1)


        pm = QPixmap(w, h)

        pm.fill(Qt.transparent)

        painter = QPainter(pm)

        painter.setRenderHint(QPainter.Antialiasing)


        # A bright, hazy cherry-blossom-morning sky. This theme's UI
        # (themes/sakura.py) uses dark text on light glass, so the
        # atmosphere behind it has to stay light too, or header text
        # sitting directly on it (no card behind it) becomes unreadable.
        sky = QLinearGradient(0, 0, 0, h)

        # Dark, moody dusk sky rather than a bright morning haze — the
        # theme's own palette is now dark-glass (white text on deep
        # plum), so the atmosphere behind it needs to match rather
        # than wash everything out.
        sky.setColorAt(0.0, QColor(43, 22, 36))

        sky.setColorAt(0.5, QColor(61, 26, 46))

        sky.setColorAt(1.0, QColor(35, 16, 28))

        painter.fillRect(0, 0, w, h, sky)


        glow = QRadialGradient(w * 0.72, h * 0.92, max(w, h) * 0.55)

        glow.setColorAt(0.0, QColor(255, 150, 90, 130))

        glow.setColorAt(0.55, QColor(255, 100, 90, 55))

        glow.setColorAt(1.0, QColor(255, 100, 90, 0))

        painter.fillRect(0, 0, w, h, QBrush(glow))

        painter.end()


        far = self._branch_layer(
            w, h, scale=0.85, x_offset=0.0, flip=False, alpha=0.4
        )

        near = self._branch_layer(
            w, h, scale=1.2, x_offset=0.0, flip=True, alpha=0.6
        )


        far = _blurred(far, radius=16)

        near = _blurred(near, radius=5)


        painter = QPainter(pm)

        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawPixmap(0, 0, far)

        painter.drawPixmap(0, 0, near)

        painter.end()


        self._atmosphere = pm

        self._atmosphere_size = (w, h)


    def paintEvent(self, event):

        if not self._initialized:

            self._init_petals()

        if self._atmosphere_size != (self.width(), self.height()):

            self._build_atmosphere()


        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawPixmap(0, 0, self._atmosphere)


        for petal in self.petals:

            painter.save()

            painter.translate(petal.x, petal.y)

            painter.rotate(petal.rotation)

            painter.setOpacity(petal.opacity)

            painter.setPen(Qt.NoPen)

            painter.setBrush(QBrush(petal.color))


            s = petal.size

            path = QPainterPath()

            path.moveTo(0, -s)

            path.quadTo(s, -s * 0.2, 0, s)

            path.quadTo(-s, -s * 0.2, 0, -s)

            painter.drawPath(path)


            painter.restore()
