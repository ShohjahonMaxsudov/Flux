from __future__ import annotations

import math
import random
from dataclasses import dataclass

from PySide6.QtCore import (
    Qt,
    QPointF,
    QRectF,
    QTimer,
)

from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
    QRadialGradient,
)

from PySide6.QtWidgets import QWidget

from themes.manager import ThemeManager


@dataclass
class Blob:
    color: QColor
    radius: float
    orbit_x: float
    orbit_y: float
    speed: float
    phase: float
    amplitude_x: float
    amplitude_y: float


@dataclass
class Ribbon:
    color: QColor
    y: float
    amp: float
    thickness: float
    speed: float
    wavelength: float
    phase: float
    tilt: float


class AuroraBackground(QWidget):

    # The atmosphere behind the UI: soft drifting colour clouds (blobs)
    # plus slow flowing aurora ribbons. What it draws comes from the
    # active theme's Atmosphere (see themes/base.py) via configure(), so
    # Dark / Nebula / Void / Ocean each get their own sky.
    #
    # Ribbons are painted into a small offscreen pixmap and scaled up
    # with smoothing - the upscale is the blur, so they stay soft and
    # cheap instead of needing a full-resolution blur pass per frame.

    RIBBON_SCALE = 5

    # 30fps is plenty for slow ambient drift, and every frame repaints the
    # whole window's worth of gradients - half the frames, half the CPU.

    FRAME_MS = 16

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self._time = 0.0

        self._blobs: list[Blob] = []

        self._ribbons: list[Ribbon] = []

        self._ribbon_buffer: QPixmap | None = None

        self.configure(
            ThemeManager.atmosphere()
        )

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self._tick
        )

        self.timer.start(self.FRAME_MS)


    def configure(self, atmosphere):

        # Rebuild blobs and ribbons from a theme's Atmosphere. The clock
        # keeps running, so switching themes doesn't restart the motion.

        self._blobs = [
            Blob(
                QColor(r, g, b, a),
                radius,
                ox,
                oy,
                speed,
                random.random() * math.pi * 2,
                ax,
                ay,
            )
            for (r, g, b, a, radius, ox, oy, speed, ax, ay)
            in atmosphere.BLOBS
        ]

        self._ribbons = [
            Ribbon(
                QColor(r, g, b, a),
                y,
                amp,
                thickness,
                speed,
                wavelength,
                phase,
                tilt,
            )
            for (r, g, b, a, y, amp, thickness, speed, wavelength, phase, tilt)
            in atmosphere.RIBBONS
        ]

        self._ribbon_buffer = None

        self.update()


    def start(self):

        if not self.timer.isActive():

            self.timer.start(self.FRAME_MS)


    def stop(self):

        self.timer.stop()



    def _tick(self):

        self._time += self.FRAME_MS / 1000.0

        self.update()



    def _blob_center(self, blob):

        width = max(
            1,
            self.width()
        )

        height = max(
            1,
            self.height()
        )


        x = (
            blob.orbit_x * width
            +
            math.sin(
                self._time * blob.speed + blob.phase
            )
            *
            blob.amplitude_x
        )


        y = (
            blob.orbit_y * height
            +
            math.cos(
                self._time * blob.speed + blob.phase
            )
            *
            blob.amplitude_y
        )


        return QPointF(
            x,
            y
        )



    def _render_ribbons(self):

        if not self._ribbons:

            return None

        k = self.RIBBON_SCALE

        w = max(8, self.width() // k)

        h = max(8, self.height() // k)

        buf = self._ribbon_buffer

        if buf is None or buf.width() != w or buf.height() != h:

            buf = QPixmap(w, h)

            self._ribbon_buffer = buf

        buf.fill(Qt.GlobalColor.transparent)

        painter = QPainter(buf)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        t = self._time

        steps = 36

        for ribbon in self._ribbons:

            points = []

            for i in range(steps + 1):

                fx = i / steps

                angle = fx * math.tau / ribbon.wavelength

                wave = (
                    math.sin(angle + t * ribbon.speed + ribbon.phase)
                    +
                    0.5 * math.sin(
                        angle * 2.1
                        + t * ribbon.speed * 1.6
                        + ribbon.phase * 1.7
                    )
                )

                yc = (
                    ribbon.y
                    + ribbon.tilt * (fx - 0.5)
                    + ribbon.amp * wave * 0.66
                ) * h

                thickness = (
                    ribbon.thickness * h
                    * (
                        0.78
                        + 0.22 * math.sin(
                            fx * 6.0
                            + t * ribbon.speed * 0.8
                            + ribbon.phase
                        )
                    )
                )

                points.append((fx * w, yc, thickness))


            # Three stacked bands, widest faintest -> narrowest brightest,
            # which reads as a soft-edged curtain of light.

            for layer_scale, layer_alpha in (
                (1.0, 0.30),
                (0.66, 0.45),
                (0.34, 0.65),
            ):

                path = QPainterPath()

                x0, y0, t0 = points[0]

                path.moveTo(x0, y0 - t0 * layer_scale / 2)

                for x, yc, th in points[1:]:

                    path.lineTo(x, yc - th * layer_scale / 2)

                for x, yc, th in reversed(points):

                    path.lineTo(x, yc + th * layer_scale / 2)

                path.closeSubpath()

                gradient = QLinearGradient(0, 0, w, 0)

                peak = ribbon.color.alpha() * layer_alpha

                for stop, strength in (
                    (0.0, 0.0),
                    (0.18, 1.0),
                    (0.82, 1.0),
                    (1.0, 0.0),
                ):

                    c = QColor(ribbon.color)

                    c.setAlpha(int(peak * strength))

                    gradient.setColorAt(stop, c)

                painter.setBrush(gradient)

                painter.drawPath(path)

        painter.end()

        return buf



    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )


        path = QPainterPath()

        path.addRect(
            QRectF(self.rect())
        )

        painter.setClipPath(
            path
        )


        # Blob radii were tuned for a ~1550px window; scale gently with
        # the actual size so a big monitor isn't left with tiny clouds.

        scale = max(
            0.7,
            min(1.5, self.width() / 1550)
        )


        for blob in self._blobs:

            center = self._blob_center(
                blob
            )

            radius = blob.radius * scale


            gradient = QRadialGradient(
                center,
                radius
            )


            color = QColor(
                blob.color
            )

            edge = QColor(
                blob.color
            )

            edge.setAlpha(0)


            gradient.setColorAt(
                0.0,
                color
            )

            gradient.setColorAt(
                1.0,
                edge
            )


            painter.setBrush(
                gradient
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )


            painter.drawEllipse(
                center,
                radius,
                radius
            )


        ribbons = self._render_ribbons()

        if ribbons is not None:

            painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform
            )

            painter.drawPixmap(
                self.rect(),
                ribbons
            )


        painter.end()
