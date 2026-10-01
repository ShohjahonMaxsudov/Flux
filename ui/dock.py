from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QPushButton, QLabel, QHBoxLayout, QVBoxLayout

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
        self.setFixedSize(64, 56)
        self.setToolTip(label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 4)
        layout.setSpacing(1)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = IconGlyph(icon_name, size=20, stroke_width=1.8)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.label.hide()

        layout.addWidget(self.icon, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.clicked.connect(lambda: self.activated.emit(self.key))
        self.apply_theme()

    def set_active(self, active):
        self.active = bool(active)
        self.label.setVisible(self.active)
        self.apply_theme()

    def apply_theme(self):
        theme = ThemeManager.get()

        if self.active:
            background = (
                "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                f"stop:0 {rgba(theme.Colors.PRIMARY, 0.42)}, "
                f"stop:0.58 {rgba(theme.Colors.PRIMARY, 0.20)}, "
                f"stop:1 {rgba(theme.Colors.PURPLE, 0.14)})"
            )
            border = rgba(theme.Colors.PRIMARY, 0.58)
            icon_color = theme.Colors.TEXT
            text_color = theme.Colors.TEXT
        else:
            background = "transparent"
            border = "transparent"
            icon_color = theme.Colors.TEXT_SECONDARY
            text_color = theme.Colors.TEXT_SECONDARY

        self.setStyleSheet(
            f"""
            QPushButton {{
                background: {background};
                border: 1px solid {border};
                border-radius: 18px;
            }}
            QPushButton:hover {{
                background: {theme.Colors.GLASS_HOVER};
                border: 1px solid {rgba(theme.Colors.TEXT, 0.10)};
            }}
            """
        )

        self.icon.setColor(icon_color)
        self.label.setStyleSheet(
            f"color:{text_color}; font-size:9px; font-weight:700; background:transparent; border:none;"
        )


class FrostedDockBackdrop(QFrame):
    """Live frosted sampling of Flux's animated theme background."""

    def __init__(self, providers, parent=None):
        super().__init__(parent)
        self.providers = list(providers)
        self._snapshot = QPixmap()
        self._reduce_motion = False

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setFixedSize(520, 76)

        self._timer = QTimer(self)
        self._timer.setInterval(90)
        self._timer.timeout.connect(self.refresh_snapshot)
        self._timer.start()

        self.apply_theme()

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
        if not self.isVisible() or self.width() < 4 or self.height() < 4:
            return

        canvas = QPixmap(self.size())
        canvas.fill(Qt.GlobalColor.transparent)

        theme = ThemeManager.get()
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        base = QLinearGradient(0, 0, 0, self.height())
        base.setColorAt(0.0, QColor(theme.Colors.SECONDARY))
        base.setColorAt(1.0, QColor(theme.Colors.BACKGROUND))
        painter.fillRect(canvas.rect(), base)

        source_rect = self.geometry()
        for provider in self.providers:
            if provider is None or not provider.isVisible():
                continue
            try:
                pixmap = provider.grab(source_rect)
            except Exception:
                continue
            if not pixmap.isNull():
                painter.drawPixmap(0, 0, pixmap)

        painter.end()

        # Downsample + smooth reconstruction gives a light, live frosted
        # effect without relying on platform-specific backdrop blur APIs.
        tiny_w = max(24, self.width() // 8)
        tiny_h = max(8, self.height() // 8)
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

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 28, 28)
        painter.setClipPath(path)

        if not self._snapshot.isNull():
            painter.drawPixmap(self.rect(), self._snapshot)

        # Flux-specific veil: dense edges for legibility, a clearer center
        # so the active animated theme is still visible through the glass.
        veil = QLinearGradient(0, 0, self.width(), 0)
        edge = QColor(theme.Colors.BACKGROUND)
        edge.setAlpha(178)
        middle = QColor(theme.Colors.SECONDARY)
        middle.setAlpha(116)
        accent = QColor(theme.Colors.PRIMARY)
        accent.setAlpha(28)
        veil.setColorAt(0.0, edge)
        veil.setColorAt(0.38, middle)
        veil.setColorAt(0.58, accent)
        veil.setColorAt(1.0, edge)
        painter.fillPath(path, veil)

        sheen = QLinearGradient(0, 0, 0, self.height())
        top = QColor(theme.Colors.TEXT)
        top.setAlpha(24)
        bottom = QColor(theme.Colors.BACKGROUND)
        bottom.setAlpha(28)
        sheen.setColorAt(0.0, top)
        sheen.setColorAt(0.30, QColor(255, 255, 255, 0))
        sheen.setColorAt(1.0, bottom)
        painter.fillPath(path, sheen)

        painter.setClipping(False)
        rim = QColor(theme.Colors.TEXT)
        rim.setAlpha(38)
        painter.setPen(QPen(rim, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)


class FloatingDock(QFrame):
    pageChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(520, 76)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.progress = 0.0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(6)

        self.buttons = []
        self._by_key = {}

        items = [
            ("home", "Home", "Dashboard"),
            ("tasks", "Tasks", "Tasks"),
            ("timer", "Focus", "Focus"),
            ("calendar", "Calendar", "Calendar"),
            ("notebook", "Notes", "Notes"),
            ("chart", "Stats", "Statistics"),
        ]

        for icon_name, label, key in items:
            button = DockButton(icon_name, label, key, self)
            button.activated.connect(self._activate)
            self.buttons.append(button)
            self._by_key[key] = button
            layout.addWidget(button)

        self.separator = QFrame(self)
        self.separator.setFixedSize(1, 30)
        layout.addSpacing(2)
        layout.addWidget(self.separator, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addSpacing(2)

        settings = DockButton("gear", "Settings", "Settings", self)
        settings.activated.connect(self._activate)
        self.buttons.append(settings)
        self._by_key["Settings"] = settings
        layout.addWidget(settings)

        self.set_active("Dashboard")
        self.apply_theme()

    def _activate(self, key):
        self.set_active(key)
        self.pageChanged.emit(key)

    def set_active(self, key):
        for button in self.buttons:
            button.set_active(button.key == key)
        self.update()

    def set_progress(self, percent):
        try:
            value = float(percent) / 100.0
        except (TypeError, ValueError):
            value = 0.0
        self.progress = max(0.0, min(1.0, value))
        self.update()

    def apply_theme(self):
        theme = ThemeManager.get()
        self.setStyleSheet("QFrame { background: transparent; border: none; }")
        self.separator.setStyleSheet(
            f"background:{rgba(theme.Colors.TEXT, 0.14)}; border:none;"
        )
        for button in self.buttons:
            button.apply_theme()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        theme = ThemeManager.get()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Flux signal: deliberately different from the wide selected capsule
        # used by social-app docks.
        signal = QColor(theme.Colors.PRIMARY)
        signal.setAlpha(190)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(signal)
        painter.drawRoundedRect(self.width() // 2 - 16, 4, 32, 2, 1, 1)

        # Preserve Today's Progress from the old sidebar as a quiet rail.
        rail_x = 24
        rail_w = self.width() - 48
        rail_y = self.height() - 4
        rail = QColor(theme.Colors.TEXT)
        rail.setAlpha(18)
        painter.setBrush(rail)
        painter.drawRoundedRect(rail_x, rail_y, rail_w, 2, 1, 1)

        if self.progress > 0:
            fill = QLinearGradient(rail_x, 0, rail_x + rail_w, 0)
            p = QColor(theme.Colors.PRIMARY)
            p.setAlpha(190)
            q = QColor(theme.Colors.PURPLE)
            q.setAlpha(170)
            fill.setColorAt(0.0, p)
            fill.setColorAt(1.0, q)
            painter.setBrush(fill)
            painter.drawRoundedRect(
                rail_x,
                rail_y,
                max(2, int(rail_w * self.progress)),
                2,
                1,
                1,
            )
