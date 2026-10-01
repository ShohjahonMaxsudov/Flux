from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget

from themes.manager import ThemeManager


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
# DRIFTER  (bubbles / embers / snow / fireflies)
# ---------------------------------------------------------

@dataclass
class Bubble:
    x: float
    y: float
    radius: float
    rise: float
    sway: float
    phase: float
    alpha: float


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

        self.speed = random.uniform(36.0, 52.0)

        self.life = 0
        self.max_life = random.randint(20, 33)

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
# PARTICLE WIDGET
# ---------------------------------------------------------

class StarField(QWidget):
    """
    Transparent animated particle layer: twinkling stars (plus the odd
    shooting star), or slowly rising bubbles for the Ocean theme.

    Put above AuroraBackground and below the UI. What it draws comes
    from the active theme's Atmosphere via configure().
    """

    STAR_COUNT = 140

    # 30fps: motion below is expressed per-tick, tuned for this rate.

    FRAME_MS = 33

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._time = 0.0

        self.mode = "stars"

        self.alpha_scale = 1.0

        self.tint = (255, 255, 255)

        self.shooting_enabled = True

        self.shoot_frames = (450, 1200)

        self.stars: list[Star] = []
        self.bubbles: list[Bubble] = []
        self.shooting: ShootingStar | None = None

        self._frames_until_shoot = random.randint(*self.shoot_frames)

        self.configure(ThemeManager.atmosphere())

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self.FRAME_MS)


    def configure(self, atmosphere):

        self.mode = atmosphere.PARTICLES

        self.STAR_COUNT = atmosphere.PARTICLE_COUNT

        self.alpha_scale = atmosphere.PARTICLE_ALPHA

        self.tint = tuple(atmosphere.PARTICLE_COLOR)

        self.shooting_enabled = (
            atmosphere.SHOOTING_STARS
            and self.mode == "stars"
        )

        self.shoot_frames = tuple(atmosphere.SHOOT_FRAMES)

        self._frames_until_shoot = random.randint(*self.shoot_frames)

        self.shooting = None

        self._create_particles()

        self.update()


    def start(self):

        if not self.timer.isActive():

            self.timer.start(self.FRAME_MS)


    def stop(self):

        self.timer.stop()

    # -----------------------------------------------------

    def _create_particles(self):
        self.stars.clear()
        self.bubbles.clear()

        w = max(self.width(), 1800)
        h = max(self.height(), 1000)

        if self.mode == "stars":

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

        elif self.mode in ("bubbles", "embers", "snow", "fireflies"):

            for _ in range(self.STAR_COUNT):

                if self.mode == "bubbles":

                    kw = dict(radius=random.uniform(2.0, 7.5), rise=random.uniform(0.18, 0.55), sway=random.uniform(6, 22))

                elif self.mode == "embers":

                    kw = dict(radius=random.uniform(0.9, 2.4), rise=random.uniform(0.5, 1.5), sway=random.uniform(10, 40))

                elif self.mode == "snow":

                    kw = dict(radius=random.uniform(0.9, 3.3), rise=random.uniform(0.3, 1.0), sway=random.uniform(8, 26))

                else:

                    kw = dict(radius=random.uniform(1.3, 2.1), rise=0.0, sway=random.uniform(28, 75))

                self.bubbles.append(
                    Bubble(
                        x=random.uniform(0, w),
                        y=random.uniform(0, h),
                        phase=random.uniform(0, math.pi * 2),
                        alpha=random.uniform(0.35, 1.0),
                        **kw
                    )
                )

    # -----------------------------------------------------

    def resizeEvent(self, event):
        self._create_particles()
        super().resizeEvent(event)

    # -----------------------------------------------------

    def _tick(self):
        self._time += self.FRAME_MS / 1000.0

        if self.mode in ("bubbles", "embers", "snow"):

            h = max(self.height(), 1)

            w = max(self.width(), 1)

            for b in self.bubbles:

                if self.mode == "snow":

                    b.y += b.rise * 2

                    if b.y > h + 12:

                        b.y = -12

                        b.x = random.uniform(0, w)

                else:

                    b.y -= b.rise * 2

                    if b.y < -20:

                        b.y = h + random.uniform(10, 80)

                        b.x = random.uniform(0, w)

        if self.shooting_enabled:

            self._frames_until_shoot -= 1

            if self._frames_until_shoot <= 0:
                self.shooting = ShootingStar(self.width(), self.height())
                self._frames_until_shoot = random.randint(*self.shoot_frames)

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

        r, g, b = self.tint

        # ------------------------
        # Stars
        # ------------------------

        for star in self.stars:

            alpha = (
                star.base_alpha
                + math.sin(self._time * star.speed + star.phase) * 55
            ) * self.alpha_scale

            alpha = max(14, min(255, int(alpha)))

            # The few bigger stars get a faint halo.
            if star.radius > 1.7:

                painter.setBrush(QColor(r, g, b, int(alpha * 0.12)))

                painter.drawEllipse(
                    QPointF(star.x, star.y),
                    star.radius * 3.2,
                    star.radius * 3.2,
                )

            painter.setBrush(QColor(r, g, b, alpha))

            painter.drawEllipse(
                QPointF(star.x, star.y),
                star.radius,
                star.radius,
            )

        # ------------------------
        # Drifters
        # ------------------------

        h_total = max(self.height(), 1)

        for bub in self.bubbles:

            a = bub.alpha * self.alpha_scale

            if self.mode == "bubbles":

                cx = bub.x + math.sin(self._time * 0.9 + bub.phase) * bub.sway

                painter.setBrush(QColor(r, g, b, int(255 * a * 0.07)))

                painter.setPen(QPen(QColor(r, g, b, int(255 * a * 0.45)), 1))

                painter.drawEllipse(QPointF(cx, bub.y), bub.radius, bub.radius)

                painter.setPen(Qt.PenStyle.NoPen)

                painter.setBrush(QColor(255, 255, 255, int(255 * a * 0.55)))

                painter.drawEllipse(
                    QPointF(cx - bub.radius * 0.35, bub.y - bub.radius * 0.35),
                    max(0.6, bub.radius * 0.18),
                    max(0.6, bub.radius * 0.18),
                )

            elif self.mode == "embers":

                cx = bub.x + math.sin(self._time * 0.7 + bub.phase) * bub.sway

                flicker = 0.6 + 0.4 * math.sin(self._time * 7 + bub.phase * 3)

                fade = max(0.0, min(1.0, bub.y / h_total)) ** 0.6

                ea = a * flicker * fade

                halo = QRadialGradient(QPointF(cx, bub.y), bub.radius * 6)

                halo.setColorAt(0.0, QColor(r, g, b, int(255 * ea * 0.35)))

                halo.setColorAt(1.0, QColor(r, g, b, 0))

                painter.setPen(Qt.PenStyle.NoPen)

                painter.setBrush(halo)

                painter.drawEllipse(QPointF(cx, bub.y), bub.radius * 6, bub.radius * 6)

                painter.setBrush(QColor(255, 236, 190, int(255 * min(1.0, ea))))

                painter.drawEllipse(QPointF(cx, bub.y), bub.radius, bub.radius)

            elif self.mode == "snow":

                cx = bub.x + math.sin(self._time * 0.6 + bub.phase) * bub.sway

                painter.setPen(Qt.PenStyle.NoPen)

                if bub.radius > 2.2:

                    painter.setBrush(QColor(r, g, b, int(255 * a * 0.12)))

                    painter.drawEllipse(QPointF(cx, bub.y), bub.radius * 2.2, bub.radius * 2.2)

                painter.setBrush(QColor(r, g, b, int(255 * a * 0.85)))

                painter.drawEllipse(QPointF(cx, bub.y), bub.radius, bub.radius)

            elif self.mode == "fireflies":

                t = self._time

                cx = bub.x + math.sin(t * 0.37 + bub.phase) * bub.sway

                cy = bub.y + math.cos(t * 0.29 + bub.phase * 1.3) * bub.sway * 0.7

                pulse = max(0.0, math.sin(t * 0.9 + bub.phase * 2.0)) ** 2

                fa = a * (0.15 + 0.85 * pulse)

                halo = QRadialGradient(QPointF(cx, cy), 14)

                halo.setColorAt(0.0, QColor(r, g, b, int(255 * fa * 0.55)))

                halo.setColorAt(1.0, QColor(r, g, b, 0))

                painter.setPen(Qt.PenStyle.NoPen)

                painter.setBrush(halo)

                painter.drawEllipse(QPointF(cx, cy), 14, 14)

                painter.setBrush(QColor(255, 255, 200, int(255 * min(1.0, fa + 0.1))))

                painter.drawEllipse(QPointF(cx, cy), bub.radius, bub.radius)

        painter.setPen(Qt.PenStyle.NoPen)

        # ------------------------
        # Shooting Star
        # ------------------------

        if self.shooting:

            s = self.shooting

            tail_x = s.x - s.length
            tail_y = s.y - s.length * 0.42

            gradient = QLinearGradient(tail_x, tail_y, s.x, s.y)

            gradient.setColorAt(0.0, QColor(r, g, b, 0))

            gradient.setColorAt(1.0, QColor(r, g, b, s.alpha))

            pen = QPen(
                QBrush(gradient),
                2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )

            painter.setPen(pen)

            painter.drawLine(
                QPointF(tail_x, tail_y),
                QPointF(s.x, s.y),
            )

            painter.setBrush(QColor(r, g, b, s.alpha))

            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawEllipse(
                QPointF(s.x, s.y),
                2.6,
                2.6,
            )

        painter.end()
