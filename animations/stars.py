from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


# ---------------------------------------------------------
# STAR
# ---------------------------------------------------------

@dataclass
class Star:
    x: float
    y: float
    radius: float
    base_alpha: int
    phase: float
    speed: float


# ---------------------------------------------------------
# SHOOTING STAR
# ---------------------------------------------------------

class ShootingStar:
    def __init__(self, width: int, height: int):
        self.reset(width, height)

    def reset(self, width: int, height: int):
        self.x = random.uniform(-width * 0.2, width * 0.6)
        self.y = random.uniform(0, height * 0.45)

        self.length = random.randint(140, 240)

        self.speed = random.uniform(18.0, 26.0)

        self.life = 0
        self.max_life = random.randint(40, 65)

        self.active = True

    def update(self):
        if not self.active:
            return

        self.x += self.speed
        self.y += self.speed * 0.42

        self.life += 1

        if self.life >= self.max_life:
            self.active = False

    @property
    def alpha(self):
        return max(0, int(255 * (1 - self.life / self.max_life)))


# ---------------------------------------------------------
# STARS WIDGET
# ---------------------------------------------------------

class StarField(QWidget):
    """
    Transparent animated star layer.

    Put above AuroraBackground and below the UI.
    """

    STAR_COUNT = 140

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._time = 0.0

        self.stars: list[Star] = []
        self.shooting: ShootingStar | None = None

        self._create_stars()

        self._frames_until_shoot = random.randint(900, 2400)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)


    def start(self):

        if not self.timer.isActive():

            self.timer.start(16)


    def stop(self):

        self.timer.stop()

    # -----------------------------------------------------

    def _create_stars(self):
        self.stars.clear()

        w = max(self.width(), 1800)
        h = max(self.height(), 1000)

        for _ in range(self.STAR_COUNT):
            self.stars.append(
                Star(
                    x=random.uniform(0, w),
                    y=random.uniform(0, h),
                    radius=random.uniform(0.7, 2.2),
                    base_alpha=random.randint(80, 220),
                    phase=random.uniform(0, math.pi * 2),
                    speed=random.uniform(0.4, 1.2),
                )
            )

    # -----------------------------------------------------

    def resizeEvent(self, event):
        self._create_stars()
        super().resizeEvent(event)

    # -----------------------------------------------------

    def _tick(self):
        self._time += 0.016

        self._frames_until_shoot -= 1

        if self._frames_until_shoot <= 0:
            self.shooting = ShootingStar(self.width(), self.height())
            self._frames_until_shoot = random.randint(900, 2400)

        if self.shooting:
            self.shooting.update()

            if not self.shooting.active:
                self.shooting = None

        self.update()

    # -----------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)

        # ------------------------
        # Stars
        # ------------------------

        for star in self.stars:

            alpha = star.base_alpha + math.sin(
                self._time * star.speed + star.phase
            ) * 55

            alpha = max(25, min(255, int(alpha)))

            painter.setBrush(QColor(255, 255, 255, alpha))

            painter.drawEllipse(
                QPointF(star.x, star.y),
                star.radius,
                star.radius,
            )

        # ------------------------
        # Shooting Star
        # ------------------------

        if self.shooting:

            s = self.shooting

            tail_x = s.x - s.length
            tail_y = s.y - s.length * 0.42

            pen = QPen(
                QColor(255, 255, 255, s.alpha),
                2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )

            painter.setPen(pen)

            painter.drawLine(
                int(tail_x),
                int(tail_y),
                int(s.x),
                int(s.y),
            )

            painter.setBrush(QColor(255, 255, 255, s.alpha))

            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawEllipse(
                QPointF(s.x, s.y),
                2.6,
                2.6,
            )

        painter.end()