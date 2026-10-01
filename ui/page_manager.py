from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedWidget


class PageManager(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.pages = {}
        self._animation = None
        self._reduce_motion = False

    def add_page(self, name, widget):
        self.pages[name] = widget
        self.addWidget(widget)

    def set_reduce_motion(self, enabled):
        self._reduce_motion = bool(enabled)

    def show_page(self, name, animate=True):
        if name not in self.pages:
            return

        target = self.pages[name]

        if self.currentWidget() is target:
            return

        if self._animation is not None:
            self._animation.stop()
            self._animation = None

        self.setCurrentWidget(target)

        if self._reduce_motion or not animate:
            target.setGraphicsEffect(None)
            return

        effect = QGraphicsOpacityEffect(target)
        effect.setOpacity(0.0)
        target.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(190)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def finish():
            if target.graphicsEffect() is effect:
                target.setGraphicsEffect(None)
            if self._animation is animation:
                self._animation = None

        animation.finished.connect(finish)
        self._animation = animation
        animation.start()
