from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QWidget


class ProgressRing(QWidget):

    # A real drawn circular progress arc with the percentage centered
    # inside it — the sidebar previously just showed static "0%" text,
    # never an actual ring, and was never wired to real data at all.

    def __init__(self, parent=None, diameter=110, thickness=9):

        super().__init__(parent)

        self._value = 0

        self._track_color = QColor(255, 255, 255, 40)

        self._arc_color = QColor("#FF4D94")

        self._text_color = QColor("white")

        self._thickness = thickness

        self.setFixedSize(diameter, diameter)



    def setValue(self, value):

        value = max(0, min(100, int(value)))

        if value != self._value:

            self._value = value

            self.update()



    def setColors(self, arc_color, track_color=None, text_color=None):

        self._arc_color = QColor(arc_color)

        if track_color is not None:

            self._track_color = QColor(track_color)

        if text_color is not None:

            self._text_color = QColor(text_color)

        self.update()



    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)


        rect = QRectF(
            self._thickness / 2,
            self._thickness / 2,
            self.width() - self._thickness,
            self.height() - self._thickness
        )


        track_pen = QPen(self._track_color)

        track_pen.setWidth(self._thickness)

        track_pen.setCapStyle(Qt.RoundCap)

        painter.setPen(track_pen)

        painter.drawArc(rect, 0, 360 * 16)


        if self._value > 0:

            arc_pen = QPen(self._arc_color)

            arc_pen.setWidth(self._thickness)

            arc_pen.setCapStyle(Qt.RoundCap)

            painter.setPen(arc_pen)

            span = int(360 * 16 * (self._value / 100))

            # Start at 12 o'clock (90° in Qt's 0=3-o'clock, CCW-positive
            # coordinate system) and sweep clockwise.
            painter.drawArc(rect, 90 * 16, -span)


        painter.setPen(self._text_color)

        font = QFont()

        font.setPixelSize(int(self.width() * 0.22))

        font.setWeight(QFont.Weight(700))

        painter.setFont(font)

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            f"{self._value}%"
        )
