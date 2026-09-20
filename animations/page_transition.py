from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve
)

from PySide6.QtWidgets import QGraphicsOpacityEffect



class PageTransition:


    def __init__(
        self,
        widget
    ):

        self.widget = widget


        self.effect = QGraphicsOpacityEffect(
            widget
        )


        widget.setGraphicsEffect(
            self.effect
        )


        self.animation = QPropertyAnimation(
            self.effect,
            b"opacity"
        )


        self.animation.setDuration(
            300
        )


        self.animation.setEasingCurve(
            QEasingCurve.OutCubic
        )



    def play(self):


        self.animation.stop()


        self.animation.setStartValue(
            0
        )


        self.animation.setEndValue(
            1
        )


        self.animation.start()