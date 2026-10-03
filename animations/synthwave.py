from __future__ import annotations

import math
import time

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget


class SynthwaveBackground(QWidget):

    # The Synthwave theme's sky and floor: a striped neon sun sinking into
    # the horizon, a glowing perspective grid that scrolls toward you, and
    # a pink haze where they meet. Stars come from the StarField layer.

    FRAME_MS = 16

    HORIZON = 0.80

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._time = 0.0

        self._last_tick = None

        self._sun = None

        self._sun_key = None

        self.timer = QTimer(self)

        self.timer.timeout.connect(self._tick)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)

    def start(self):

        if not self.timer.isActive():

            self._last_tick = time.perf_counter()

            self.timer.start(self.FRAME_MS)

    def stop(self):

        self.timer.stop()

        self._last_tick = None

    def _tick(self):

        now = time.perf_counter()

        dt = (
            self.FRAME_MS / 1000.0
            if self._last_tick is None
            else max(
                0.001,
                min(
                    0.050,
                    now - self._last_tick
                )
            )
        )

        self._last_tick = now

        self._time += dt

        self.update()

    # -----------------------------------------------------

    def _sun_pixmap(self, radius):

        # Painted once per size: a vertical yellow -> pink disc with the
        # classic horizontal cut-outs, wider toward the bottom.

        if self._sun is not None and self._sun_key == radius:

            return self._sun

        size = int(radius * 2)

        pm = QPixmap(size, size)

        pm.fill(Qt.GlobalColor.transparent)

        p = QPainter(pm)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, size)

        gradient.setColorAt(0.0, QColor(255, 226, 70))

        gradient.setColorAt(0.5, QColor(255, 112, 90))

        gradient.setColorAt(1.0, QColor(255, 36, 150))

        p.setPen(Qt.PenStyle.NoPen)

        p.setBrush(gradient)

        p.drawEllipse(QRectF(0, 0, size, size))

        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)

        p.setBrush(QColor(0, 0, 0, 255))

        for i in range(7):

            top = size * (0.50 + i * 0.072)

            p.drawRect(QRectF(0, top, size, 2.0 + i * 1.9))

        p.end()

        self._sun = pm

        self._sun_key = radius

        return pm

    def paintEvent(self, event):

        w, h = self.width(), self.height()

        if w < 10 or h < 10:

            return

        horizon = h * self.HORIZON

        t = self._time

        p = QPainter(self)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # haze hugging the horizon

        haze = QLinearGradient(0, horizon - h * 0.34, 0, horizon)

        haze.setColorAt(0.0, QColor(255, 46, 151, 0))

        haze.setColorAt(1.0, QColor(255, 60, 160, 52))

        p.fillRect(QRectF(0, horizon - h * 0.34, w, h * 0.34), haze)

        # sun, breathing gently

        radius = int(h * 0.16)

        centre = QPointF(w * 0.88, horizon - radius * 0.12)

        glow = QRadialGradient(centre, radius * 2.4)

        glow.setColorAt(0.0, QColor(255, 60, 160, int(58 + 14 * math.sin(t * 0.8))))

        glow.setColorAt(1.0, QColor(255, 60, 160, 0))

        p.setPen(Qt.PenStyle.NoPen)

        p.setBrush(glow)

        p.drawEllipse(centre, radius * 2.4, radius * 2.4)

        p.setOpacity(0.50 + 0.07 * math.sin(t * 0.8))

        p.drawPixmap(int(centre.x() - radius), int(centre.y() - radius), self._sun_pixmap(radius))

        p.setOpacity(1.0)

        # ground

        floor = QLinearGradient(0, horizon, 0, h)

        floor.setColorAt(0.0, QColor(20, 6, 38, 232))

        floor.setColorAt(1.0, QColor(8, 2, 20, 246))

        p.fillRect(QRectF(0, horizon, w, h - horizon), floor)

        # grid: rows accelerate toward the viewer, columns fan out from the
        # vanishing point

        span = h - horizon

        offset = (t * 0.32) % 1.0

        rows = 15

        for k in range(rows + 1):

            f = (k + offset) / rows

            if f > 1.0:

                continue

            y = horizon + span * (f ** 2.2)

            alpha = int(24 + 120 * f)

            p.setPen(QPen(QColor(255, 46, 151, alpha // 4), 3.2))

            p.drawLine(QPointF(0, y), QPointF(w, y))

            p.setPen(QPen(QColor(255, 90, 190, alpha), 1.1))

            p.drawLine(QPointF(0, y), QPointF(w, y))

        vx = w * 0.5

        for i in range(-22, 23):

            x_top = vx + i * w * 0.012

            x_bottom = vx + i * w * 0.115

            p.setPen(QPen(QColor(178, 102, 255, 34), 3.0))

            p.drawLine(QPointF(x_top, horizon), QPointF(x_bottom, h))

            p.setPen(QPen(QColor(190, 130, 255, 84), 1.0))

            p.drawLine(QPointF(x_top, horizon), QPointF(x_bottom, h))

        # bright horizon line

        p.setPen(QPen(QColor(255, 60, 170, 70), 7.0))

        p.drawLine(QPointF(0, horizon), QPointF(w, horizon))

        p.setPen(QPen(QColor(255, 170, 230, 220), 1.6))

        p.drawLine(QPointF(0, horizon), QPointF(w, horizon))

        p.end()
