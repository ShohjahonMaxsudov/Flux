from PySide6.QtCore import Qt, Signal, QTimer, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout

from themes.manager import ThemeManager
from utils.color_utils import rgba
from ui.icons import IconGlyph


class DockButton(QPushButton):
    activated = Signal(str)

    def __init__(self, icon_name, label, key, parent=None):
        super().__init__(parent)
        self.key = key
        self.active = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(70, 60)
        self.setToolTip(label)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

        self.icon = IconGlyph(icon_name, size=32, stroke_width=1.9)
        self.icon.setParent(self)
        self.icon.setFixedSize(40, 40)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.clicked.connect(lambda: self.activated.emit(self.key))
        self.apply_theme()

    def resizeEvent(self, event):
        self.icon.move(
            (self.width() - self.icon.width()) // 2,
            (self.height() - self.icon.height()) // 2,
        )
        super().resizeEvent(event)

    def enterEvent(self, event):
        self._apply_icon(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_icon(False)
        super().leaveEvent(event)

    def set_active(self, active):
        self.active = bool(active)
        self._apply_icon(False)

    def _apply_icon(self, hover=False):
        theme = ThemeManager.get()

        if self.active or hover:
            color = theme.Colors.TEXT
        else:
            color = theme.Colors.TEXT_SECONDARY

        self.icon.setColor(color)

    def apply_theme(self):
        self._apply_icon(False)


class ActivePill(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.apply_theme()

    def apply_theme(self):
        theme = ThemeManager.get()
        self.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {rgba(theme.Colors.PRIMARY, 0.25)},
                    stop:0.55 {rgba(theme.Colors.PRIMARY, 0.15)},
                    stop:1 {rgba(theme.Colors.PRIMARY, 0.09)}
                );
                border: 1px solid {rgba(theme.Colors.PRIMARY, 0.58)};
                border-radius: 25px;
            }}
            """
        )


class BottomAtmosphereBlur(QFrame):
    """
    Feathered bottom atmosphere.

    Important: this intentionally does NOT grab/re-render the animated
    background. The old live capture was the main source of dock jank.
    Flux's real animated background remains visible through this translucent
    haze, while the multi-stop fade creates the soft visual separation.
    """

    HEIGHT = 210

    def __init__(self, providers=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_reduce_motion(self, enabled):
        pass

    def refresh_snapshot(self):
        # Compatibility with the earlier blur implementation.
        self.update()

    def apply_theme(self):
        self.update()

    def paintEvent(self, event):
        theme = ThemeManager.get()
        painter = QPainter(self)

        # No rectangle, no border, no hard starting edge.
        # The layer is fully transparent at its top and only becomes
        # noticeable toward the dock / bottom of the window.
        fade = QLinearGradient(0, 0, 0, self.height())

        clear = QColor(theme.Colors.BACKGROUND)
        clear.setAlpha(0)

        soft = QColor(theme.Colors.BACKGROUND)
        soft.setAlpha(24)

        medium = QColor(theme.Colors.BACKGROUND)
        medium.setAlpha(84)

        deep = QColor(theme.Colors.BACKGROUND)
        deep.setAlpha(176)

        bottom = QColor(theme.Colors.BACKGROUND)
        bottom.setAlpha(222)

        fade.setColorAt(0.00, clear)
        fade.setColorAt(0.20, clear)
        fade.setColorAt(0.42, soft)
        fade.setColorAt(0.68, medium)
        fade.setColorAt(0.88, deep)
        fade.setColorAt(1.00, bottom)

        painter.fillRect(self.rect(), fade)

        # Tiny theme-colour haze so Aurora/Sakura/etc still tint the bottom.
        accent = QLinearGradient(0, 0, self.width(), 0)

        p = QColor(theme.Colors.PRIMARY)
        p.setAlpha(0)

        p_mid = QColor(theme.Colors.PRIMARY)
        p_mid.setAlpha(16)

        q_mid = QColor(theme.Colors.PURPLE)
        q_mid.setAlpha(12)

        accent.setColorAt(0.0, p)
        accent.setColorAt(0.35, p_mid)
        accent.setColorAt(0.68, q_mid)
        accent.setColorAt(1.0, p)

        painter.setOpacity(0.55)
        painter.fillRect(self.rect(), accent)


class FloatingDock(QFrame):
    pageChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(686, 86)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._active_key = "Dashboard"
        self._indicator_animation = None

        self.indicator = ActivePill(self)
        self.indicator.setGeometry(14, 10, 80, 66)
        self.indicator.lower()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 13, 18, 13)
        layout.setSpacing(8)

        self.buttons = []
        self._by_key = {}

        items = [
            ("home", "Home", "Dashboard"),
            ("tasks", "Tasks", "Tasks"),
            ("star", "Milestones", "Milestones"),
            ("timer", "Focus", "Focus"),
            ("calendar", "Calendar", "Calendar"),
            ("notebook", "Notes", "Notes"),
            ("chart", "Statistics", "Statistics"),
        ]

        for icon_name, label, key in items:
            button = DockButton(icon_name, label, key, self)
            button.activated.connect(self._activate)
            self.buttons.append(button)
            self._by_key[key] = button
            layout.addWidget(button)

        self.separator = QFrame(self)
        self.separator.setFixedSize(1, 34)
        layout.addSpacing(2)
        layout.addWidget(self.separator, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addSpacing(2)

        settings = DockButton("gear", "Settings", "Settings", self)
        settings.activated.connect(self._activate)
        self.buttons.append(settings)
        self._by_key["Settings"] = settings
        layout.addWidget(settings)

        self.apply_theme()
        QTimer.singleShot(0, lambda: self.set_active("Dashboard", animate=False))

    def _activate(self, key):
        # App changes the page first, then updates the dock once.
        # The previous implementation animated here and again in app.py.
        self.pageChanged.emit(key)

    def _indicator_rect_for(self, button):
        return button.geometry().adjusted(-5, -3, 5, 3)

    def set_active(self, key, animate=True):
        if key not in self._by_key:
            return

        if key == self._active_key and animate:
            # Still ensure icon state is correct, but don't restart animation.
            for button in self.buttons:
                button.set_active(button.key == key)
            return

        self._active_key = key

        for button in self.buttons:
            button.set_active(button.key == key)

        target = self._indicator_rect_for(self._by_key[key])

        if self._indicator_animation is not None:
            self._indicator_animation.stop()
            self._indicator_animation = None

        if not animate or not self.isVisible():
            self.indicator.setGeometry(target)
            return

        animation = QPropertyAnimation(self.indicator, b"geometry", self)
        animation.setDuration(175)
        animation.setStartValue(self.indicator.geometry())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def finish():
            if self._indicator_animation is animation:
                self._indicator_animation = None

        animation.finished.connect(finish)
        self._indicator_animation = animation
        animation.start()

    def set_progress(self, percent):
        pass

    def apply_theme(self):
        theme = ThemeManager.get()

        self.indicator.apply_theme()

        self.separator.setStyleSheet(
            f"background:{rgba(theme.Colors.TEXT, 0.18)}; border:none;"
        )

        for button in self.buttons:
            button.apply_theme()

        self.update()

    def paintEvent(self, event):
        theme = ThemeManager.get()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 42, 42)

        glass = QLinearGradient(0, 0, 0, self.height())

        top = QColor(theme.Colors.SURFACE_ALT)
        top.setAlpha(178)

        mid = QColor(theme.Colors.SURFACE)
        mid.setAlpha(188)

        bottom = QColor(theme.Colors.BACKGROUND)
        bottom.setAlpha(214)

        glass.setColorAt(0.0, top)
        glass.setColorAt(0.50, mid)
        glass.setColorAt(1.0, bottom)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glass)
        painter.drawPath(path)

        # Theme-coloured rim, closer to the reference but still Flux.
        rim = QColor(theme.Colors.PRIMARY)
        rim.setAlpha(115)

        painter.setPen(QPen(rim, 1.25))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Soft top highlight.
        highlight = QColor(theme.Colors.TEXT)
        highlight.setAlpha(34)
        painter.setPen(QPen(highlight, 1))
        painter.drawArc(
            rect.adjusted(2, 2, -2, -2),
            24 * 16,
            132 * 16,
        )
