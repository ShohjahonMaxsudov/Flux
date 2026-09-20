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
    QPainter,
    QPainterPath,
    QRadialGradient,
)

from PySide6.QtWidgets import QWidget


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


class AuroraBackground(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self._time = 0.0


        self._blobs = [

            Blob(
                QColor(90, 125, 255, 85),
                360,
                0.22,
                0.30,
                0.17,
                random.random() * math.pi * 2,
                120,
                90,
            ),

            Blob(
                QColor(75, 232, 165, 75),
                330,
                0.72,
                0.62,
                0.13,
                random.random() * math.pi * 2,
                140,
                120,
            ),

            Blob(
                QColor(165, 110, 255, 70),
                310,
                0.56,
                0.18,
                0.20,
                random.random() * math.pi * 2,
                100,
                130,
            ),
        ]


        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self._tick
        )

        self.timer.start(16)


    def start(self):

        if not self.timer.isActive():

            self.timer.start(16)


    def stop(self):

        self.timer.stop()



    def _tick(self):

        self._time += 0.016

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


        for blob in self._blobs:

            center = self._blob_center(
                blob
            )


            gradient = QRadialGradient(
                center,
                blob.radius
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
                blob.radius,
                blob.radius
            )


        painter.end()