from PySide6.QtCore import Qt, Signal, QTimer, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QPushButton, QHBoxLayout

from themes.manager import ThemeManager
from utils.color_utils import rgba
from ui.icons import IconGlyph


class DockButton(QPushButton):
    activated = Signal(str)

    def __init__(self, icon_name, label, key, parent=None):
        super().__init__(parent)
        self.key = key
        self.label_text = label
        self.active = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(64, 54)
        self.setToolTip(label)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

        self.icon = IconGlyph(icon_name, size=28, stroke_width=1.9)
        self.icon.setParent(self)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.icon.setFixedSize(34, 34)

        self.clicked.connect(lambda: self.activated.emit(self.key))
        self.apply_theme()

    def resizeEvent(self, event):
        self.icon.move(
            (self.width() - self.icon.width()) // 2,
            (self.height() - self.icon.height()) // 2,
        )
        super().resizeEvent(event)

    def enterEvent(self, event):
        self._apply_icon(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_icon(hover=False)
        super().leaveEvent(event)

    def set_active(self, active):
        self.active = bool(active)
        self._apply_icon(hover=False)

    def _apply_icon(self, hover=False):
        theme = ThemeManager.get()

        if self.active:
            color = theme.Colors.TEXT
        elif hover:
            color = theme.Colors.TEXT
        else:
            color = theme.Colors.TEXT_SECONDARY

        self.icon.setColor(color)

    def apply_theme(self):
        self._apply_icon(hover=False)


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
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {rgba(theme.Colors.PRIMARY, 0.24)},
                    stop:0.55 {rgba(theme.Colors.PRIMARY, 0.14)},
                    stop:1 {rgba(theme.Colors.PURPLE, 0.10)}
                );
                border: 1px solid {rgba(theme.Colors.PRIMARY, 0.34)};
                border-radius: 20px;
            }}
            """
        )


class BottomAtmosphereBlur(QFrame):
    """Low-cost blurred atmosphere strip behind the floating dock."""

    HEIGHT = 152

    def __init__(self, providers, parent=None):
        super().__init__(parent)
        self.providers = list(providers)
        self._snapshot = QPixmap()
        self._reduce_motion = False

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._timer = QTimer(self)
        self._timer.setInterval(280)
        self._timer.timeout.connect(self.refresh_snapshot)
        self._timer.start()

    def set_reduce_motion(self, enabled):
        self._reduce_motion = bool(enabled)
        if self._reduce_motion:
            self._timer.stop()
            self.refresh_snapshot()
        elif not self._timer.isActive():
            self._timer.start()

    def apply_theme(self):
        self.refresh_snapshot()
        self.update()

    def refresh_snapshot(self):
        if not self.isVisible() or self.width() < 8 or self.height() < 8:
            return

        theme = ThemeManager.get()

        canvas = QPixmap(self.size())
        canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter(canvas)

        base = QLinearGradient(0, 0, 0, self.height())
        top = QColor(theme.Colors.SECONDARY)
        top.setAlpha(70)
        bottom = QColor(theme.Colors.BACKGROUND)
        bottom.setAlpha(210)
        base.setColorAt(0.0, top)
        base.setColorAt(1.0, bottom)
        painter.fillRect(canvas.rect(), base)

        # Blur only the main animated atmosphere, not every overlay.
        # Sampling one strip at ~3.5 fps is dramatically cheaper than
        # grabbing multiple widgets every 90 ms.
        for provider in self.providers:
            if provider is None or not provider.isVisible():
                continue

            source_y = max(0, provider.height() - self.height())
            source = QRect(0, source_y, provider.width(), self.height())

            try:
                pixmap = provider.grab(source)
            except Exception:
                pixmap = QPixmap()

            if not pixmap.isNull():
                painter.drawPixmap(self.rect(), pixmap)
                break

        painter.end()

        # Heavy downsample = strong blur, low CPU/GPU cost.
        tiny_w = max(48, self.width() // 14)
        tiny_h = max(8, self.height() // 14)

        tiny = canvas.scaled(
            tiny_w,
            tiny_h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self._snapshot = tiny.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.update()

    def paintEvent(self, event):
        theme = ThemeManager.get()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if not self._snapshot.isNull():
            painter.drawPixmap(self.rect(), self._snapshot)

        # Instagram-like bottom gradient behavior: invisible at the top,
        # progressively softer/darker toward the bottom.
        fade = QLinearGradient(0, 0, 0, self.height())

        c0 = QColor(theme.Colors.BACKGROUND)
        c0.setAlpha(0)

        c1 = QColor(theme.Colors.BACKGROUND)
        c1.setAlpha(55)

        c2 = QColor(theme.Colors.BACKGROUND)
        c2.setAlpha(150)

        c3 = QColor(theme.Colors.BACKGROUND)
        c3.setAlpha(220)

        fade.setColorAt(0.0, c0)
        fade.setColorAt(0.34, c1)
        fade.setColorAt(0.72, c2)
        fade.setColorAt(1.0, c3)

        painter.fillRect(self.rect(), fade)


class FloatingDock(QFrame):
    pageChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(554, 74)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._active_key = "Dashboard"
        self._indicator_animation = None

        self.indicator = ActivePill(self)
        self.indicator.setGeometry(16, 10, 64, 54)
        self.indicator.lower()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(7)

        self.buttons = []
        self._by_key = {}

        items = [
            ("home", "Home", "Dashboard"),
            ("tasks", "Tasks", "Tasks"),
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
        self.separator.setFixedSize(1, 26)
        layout.addSpacing(1)
        layout.addWidget(self.separator, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addSpacing(1)

        settings = DockButton("gear", "Settings", "Settings", self)
        settings.activated.connect(self._activate)
        self.buttons.append(settings)
        self._by_key["Settings"] = settings
        layout.addWidget(settings)

        self.apply_theme()
        QTimer.singleShot(0, lambda: self.set_active("Dashboard", animate=False))

    def _activate(self, key):
        self.set_active(key)
        self.pageChanged.emit(key)

    def _indicator_rect_for(self, button):
        return QRect(button.x(), button.y(), button.width(), button.height())

    def set_active(self, key, animate=True):
        if key not in self._by_key:
            return

        self._active_key = key

        for button in self.buttons:
            button.set_active(button.key == key)

        target = self._indicator_rect_for(self._by_key[key])

        if self._indicator_animation is not None:
            self._indicator_animation.stop()

        if not animate or not self.isVisible():
            self.indicator.setGeometry(target)
            return

        animation = QPropertyAnimation(self.indicator, b"geometry", self)
        animation.setDuration(205)
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
        # Kept for compatibility with Dashboard.progressChanged.
        # Progress no longer decorates the dock; the navigation stays minimal.
        pass

    def apply_theme(self):
        theme = ThemeManager.get()

        self.indicator.apply_theme()

        self.separator.setStyleSheet(
            f"background:{rgba(theme.Colors.TEXT, 0.13)}; border:none;"
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
        path.addRoundedRect(rect, 36, 36)

        # Clean glass surface. The real blur lives behind the dock in the
        # bottom atmosphere layer, keeping this component fast and legible.
        glass = QLinearGradient(0, 0, 0, self.height())

        top = QColor(theme.Colors.SURFACE_ALT)
        top.setAlpha(225)

        bottom = QColor(theme.Colors.BACKGROUND)
        bottom.setAlpha(238)

        glass.setColorAt(0.0, top)
        glass.setColorAt(1.0, bottom)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glass)
        painter.drawPath(path)

        rim = QColor(theme.Colors.TEXT)
        rim.setAlpha(28)

        painter.setPen(QPen(rim, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # A very restrained top highlight is enough to sell the glass.
        highlight = QColor(theme.Colors.TEXT)
        highlight.setAlpha(18)
        painter.setPen(QPen(highlight, 1))
        painter.drawLine(36, 2, self.width() - 36, 2)

        super().paintEvent(event)
