from __future__ import annotations

import math
import random

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget


class AstroBackground(QWidget):

    # The Astro theme's sky: a burning sun just off the top-left corner,
    # all eight planets in order on their orbits (Mercury -> Neptune) with
    # the asteroid belt between Mars and Jupiter, and heat rings pulsing
    # out from the sun. Stars and meteors come from the StarField layer
    # above this one.
    #
    # Orbits are concentric circles around the sun; each planet slowly
    # sways along the part of its orbit that is actually on screen, so the
    # whole system stays visible instead of planets sailing out of frame.

    FRAME_MS = 16

    # name, orbit (fraction of the window diagonal), radius px, rgb,
    # sway period in seconds, start phase, has rings
    PLANETS = (
        ("Mercury", 0.105, 3.0, (196, 190, 184), 58, 0.4, False),
        ("Venus", 0.165, 4.8, (246, 222, 164), 92, 1.9, False),
        ("Earth", 0.230, 5.2, (86, 168, 255), 128, 3.3, False),
        ("Mars", 0.295, 4.0, (232, 108, 68), 168, 5.0, False),
        ("Jupiter", 0.470, 11.5, (226, 178, 128), 250, 0.9, False),
        ("Saturn", 0.605, 9.0, (242, 216, 158), 330, 2.6, True),
        ("Uranus", 0.730, 7.0, (150, 226, 236), 430, 4.1, False),
        ("Neptune", 0.850, 6.8, (78, 118, 255), 540, 5.8, False),
    )

    BELT_ORBIT = 0.375

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._time = 0.0

        self._ranges = {}

        self._ranges_key = None

        rng = random.Random(7)

        # angle, radial jitter (-1..1), size, drift speed
        self._belt = [
            (
                rng.uniform(0, math.tau),
                rng.uniform(-1, 1),
                rng.uniform(0.6, 1.5),
                rng.uniform(0.004, 0.010),
            )
            for _ in range(120)
        ]

        self.timer = QTimer(self)

        self.timer.timeout.connect(self._tick)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)

        self.timer.start(self.FRAME_MS)

    def start(self):

        if not self.timer.isActive():

            self.timer.start(self.FRAME_MS)

    def stop(self):

        self.timer.stop()

    def _tick(self):

        self._time += self.FRAME_MS / 1000.0

        self.update()

    # -----------------------------------------------------

    def _sun(self):

        return QPointF(-0.025 * self.width(), -0.05 * self.height())

    def _reference(self):

        return math.hypot(self.width(), self.height())

    def _visible_range(self, index, radius):

        # The span of angles (0..90 deg, measured down from the +x axis)
        # for which this orbit is inside the window.

        key = (self.width(), self.height())

        if self._ranges_key != key:

            self._ranges = {}

            self._ranges_key = key

        if index in self._ranges:

            return self._ranges[index]

        sun = self._sun()

        w, h = self.width(), self.height()

        inside = []

        for step in range(0, 181):

            angle = math.radians(step * 0.5)

            x = sun.x() + radius * math.cos(angle)

            y = sun.y() + radius * math.sin(angle)

            if 24 < x < w - 24 and 24 < y < h - 24:

                inside.append(angle)

        result = (inside[0], inside[-1]) if inside else None

        self._ranges[index] = result

        return result

    def _planet_position(self, index, radius, period, phase):

        span = self._visible_range(index, radius)

        if span is None:

            return None

        lo, hi = span

        mid = (lo + hi) / 2

        half = (hi - lo) / 2

        angle = mid + half * 0.78 * math.sin(
            self._time * math.tau / period + phase
        )

        sun = self._sun()

        return QPointF(
            sun.x() + radius * math.cos(angle),
            sun.y() + radius * math.sin(angle)
        ), angle

    # -----------------------------------------------------

    def _paint_sun(self, p, w):

        sun = self._sun()

        pulse = 1.0 + 0.035 * math.sin(self._time * 0.9) + 0.018 * math.sin(self._time * 2.3)

        p.setPen(Qt.PenStyle.NoPen)

        for radius, inner_alpha, color in (
            (0.58 * w * pulse, 40, (255, 120, 30)),
            (0.32 * w * pulse, 92, (255, 160, 50)),
            (0.17 * w * pulse, 170, (255, 205, 90)),
        ):

            glow = QRadialGradient(sun, radius)

            glow.setColorAt(0.0, QColor(*color, inner_alpha))

            glow.setColorAt(1.0, QColor(*color, 0))

            p.setBrush(glow)

            p.drawEllipse(sun, radius, radius)

        # the disc itself

        disc = 0.098 * w * pulse

        core = QRadialGradient(sun, disc)

        core.setColorAt(0.0, QColor(255, 250, 225, 255))

        core.setColorAt(0.55, QColor(255, 214, 120, 245))

        core.setColorAt(1.0, QColor(255, 150, 50, 0))

        p.setBrush(core)

        p.drawEllipse(sun, disc, disc)

        # heat: rings of warmth expanding away from the sun

        for k in range(3):

            progress = ((self._time / 7.0) + k / 3.0) % 1.0

            radius = disc * 1.3 + progress * 0.52 * w

            alpha = int(38 * (1.0 - progress) ** 1.6)

            if alpha <= 0:

                continue

            p.setBrush(Qt.BrushStyle.NoBrush)

            p.setPen(QPen(QColor(255, 180, 90, alpha), 1.5 + progress * 6))

            p.drawEllipse(sun, radius, radius)

        p.setPen(Qt.PenStyle.NoPen)

    def _paint_planet(self, p, pos, radius, color, has_rings, name):

        sun = self._sun()

        dx, dy = sun.x() - pos.x(), sun.y() - pos.y()

        length = math.hypot(dx, dy) or 1.0

        focal = QPointF(
            pos.x() + dx / length * radius * 0.45,
            pos.y() + dy / length * radius * 0.45
        )

        base = QColor(*color)

        halo = QRadialGradient(pos, radius * 3.2)

        halo.setColorAt(0.0, QColor(*color, 46))

        halo.setColorAt(1.0, QColor(*color, 0))

        p.setPen(Qt.PenStyle.NoPen)

        p.setBrush(halo)

        p.drawEllipse(pos, radius * 3.2, radius * 3.2)

        if has_rings:

            p.save()

            p.translate(pos)

            p.rotate(-20)

            ring_box = QRectF(-radius * 2.15, -radius * 0.62, radius * 4.3, radius * 1.24)

            p.setBrush(Qt.BrushStyle.NoBrush)

            p.setPen(QPen(QColor(236, 214, 160, 150), 1.7))

            p.drawArc(ring_box, 0, 180 * 16)

            p.restore()

        body = QRadialGradient(pos, radius, focal)

        body.setColorAt(0.0, base.lighter(155))

        body.setColorAt(0.6, base)

        body.setColorAt(1.0, base.darker(260))

        p.setPen(Qt.PenStyle.NoPen)

        p.setBrush(body)

        p.drawEllipse(pos, radius, radius)

        if has_rings:

            p.save()

            p.translate(pos)

            p.rotate(-20)

            p.setBrush(Qt.BrushStyle.NoBrush)

            p.setPen(QPen(QColor(236, 214, 160, 190), 1.7))

            p.drawArc(
                QRectF(-radius * 2.15, -radius * 0.62, radius * 4.3, radius * 1.24),
                180 * 16,
                180 * 16
            )

            p.restore()

        if name == "Earth":

            angle = self._time * 1.2

            moon = QPointF(
                pos.x() + math.cos(angle) * radius * 2.6,
                pos.y() + math.sin(angle) * radius * 2.6
            )

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(QColor(210, 210, 214, 220))

            p.drawEllipse(moon, 1.5, 1.5)

    def paintEvent(self, event):

        w, h = self.width(), self.height()

        if w < 10 or h < 10:

            return

        p = QPainter(self)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._paint_sun(p, w)

        sun = self._sun()

        ref = self._reference()

        # orbit lines

        p.setBrush(Qt.BrushStyle.NoBrush)

        p.setPen(QPen(QColor(255, 236, 210, 20), 1.0))

        for _, orbit, *_rest in self.PLANETS:

            p.drawEllipse(sun, orbit * ref, orbit * ref)

        # asteroid belt

        belt_radius = self.BELT_ORBIT * ref

        p.setPen(Qt.PenStyle.NoPen)

        p.setBrush(QColor(214, 200, 180, 120))

        for angle, jitter, size, speed in self._belt:

            a = angle + self._time * speed

            r = belt_radius + jitter * 0.016 * ref

            x = sun.x() + r * math.cos(a)

            y = sun.y() + r * math.sin(a)

            if 0 < x < w and 0 < y < h:

                p.drawEllipse(QPointF(x, y), size, size)

        # planets, inner to outer

        for index, (name, orbit, radius, color, period, phase, rings) in enumerate(self.PLANETS):

            placed = self._planet_position(index, orbit * ref, period, phase)

            if placed is None:

                continue

            pos, _angle = placed

            self._paint_planet(p, pos, radius, color, rings, name)

        p.end()
