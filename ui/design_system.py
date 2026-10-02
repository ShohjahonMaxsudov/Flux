from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.icons import IconGlyph


class Metrics:
    PAGE_X = 24
    PAGE_Y = 22
    GAP = 16
    CARD_RADIUS = 16
    CONTROL_RADIUS = 11
    SIDEBAR_WIDTH = 222


class SurfaceCard(QFrame):
    """Consistent Flux surface used by every v3 dashboard/task card."""

    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("fluxSurfaceCard")

        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(18, 16, 18, 16)
        self.body.setSpacing(11)

        self.title_label = None
        self.subtitle_label = None

        self.header_row = None
        self.header_action = None

        if title:
            self.header_row = QHBoxLayout()
            self.header_row.setSpacing(10)

            titles = QVBoxLayout()
            titles.setSpacing(2)

            self.title_label = QLabel(title)
            self.title_label.setObjectName("surfaceTitle")
            titles.addWidget(self.title_label)

            if subtitle:
                self.subtitle_label = QLabel(subtitle)
                self.subtitle_label.setObjectName("surfaceSubtitle")
                titles.addWidget(self.subtitle_label)

            self.header_row.addLayout(titles, 1)

            self.header_action = QHBoxLayout()
            self.header_action.setContentsMargins(0, 0, 0, 0)
            self.header_action.setSpacing(6)
            self.header_row.addLayout(self.header_action)

            self.body.addLayout(self.header_row)

        SurfaceCard.apply_theme(self)

    def set_header_action(self, widget):
        if self.header_action is None:
            return

        while self.header_action.count():
            item = self.header_action.takeAt(0)
            old = item.widget()
            if old:
                old.hide()
                old.setParent(None)
                old.deleteLater()

        self.header_action.addWidget(
            widget,
            0,
            Qt.AlignmentFlag.AlignTop
        )

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.setStyleSheet(
            f"""
            QFrame#fluxSurfaceCard {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:{Metrics.CARD_RADIUS}px;
            }}
            QLabel#surfaceTitle {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:16px;
                font-weight:700;
            }}
            QLabel#surfaceSubtitle {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:11px;
            }}
            """
        )


class HeaderPill(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("headerPill")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(30)
        self.apply_theme()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.setStyleSheet(
            f"""
            QPushButton#headerPill {{
                color:{c.TEXT};
                background:rgba(40,54,76,0.72);
                border:1px solid {c.BORDER};
                border-radius:9px;
                padding:5px 11px;
                font-size:10px;
            }}
            QPushButton#headerPill:hover {{
                background:{c.SURFACE_ALT};
                border-color:rgba(115,150,220,0.36);
            }}
            """
        )


class HeaderLink(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setObjectName("headerLink")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(28)

        row = QHBoxLayout(self)
        row.setContentsMargins(7, 0, 5, 0)
        row.setSpacing(5)

        self.label = QLabel(text)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.icon = IconGlyph("arrow_right", size=13)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        row.addWidget(self.label)
        row.addWidget(self.icon)
        self.apply_theme()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.icon.setColor(c.TEXT_SECONDARY)
        self.label.setStyleSheet(
            f"color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px;"
        )
        self.setStyleSheet(
            """
            QPushButton#headerLink {
                background:transparent;
                border:none;
                border-radius:7px;
            }
            QPushButton#headerLink:hover {
                background:rgba(100,125,170,0.10);
            }
            """
        )


class ClickableFrame(QFrame):
    clicked = Signal()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class IconCircle(QFrame):
    def __init__(self, icon_name, diameter=42, parent=None):
        super().__init__(parent)
        self.setObjectName("iconCircle")
        self.setFixedSize(diameter, diameter)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = IconGlyph(icon_name, size=max(16, diameter // 2))
        layout.addWidget(self.icon)
        self.apply_theme()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.icon.setColor(c.PRIMARY_LIGHT)
        self.setStyleSheet(
            f"""
            QFrame#iconCircle {{
                background:rgba(76,114,255,0.14);
                border:1px solid rgba(102,145,255,0.20);
                border-radius:{self.width() // 2}px;
            }}
            """
        )


class CheckButton(QPushButton):
    def __init__(self, checked=False, size=24, square=False, parent=None):
        super().__init__(parent)
        self._checked_visual = bool(checked)
        self._square = bool(square)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("fluxCheckButton")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(max(3, size // 5), max(3, size // 5), max(3, size // 5), max(3, size // 5))
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = IconGlyph("check", size=max(10, int(size * 0.52)), stroke_width=2.2)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self.icon)

        self.apply_theme()

    def set_checked_visual(self, checked):
        self._checked_visual = bool(checked)
        self.apply_theme()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        radius = 6 if self._square else self.width() // 2

        self.icon.setVisible(self._checked_visual)
        self.icon.setColor("#FFFFFF")

        background = c.PRIMARY if self._checked_visual else "transparent"
        border = c.PRIMARY_LIGHT if self._checked_visual else "#60738E"

        self.setStyleSheet(
            f"""
            QPushButton#fluxCheckButton {{
                background:{background};
                border:1px solid {border};
                border-radius:{radius}px;
            }}
            QPushButton#fluxCheckButton:hover {{
                border-color:{c.PRIMARY_LIGHT};
                background:rgba(79,103,244,0.16);
            }}
            """
        )


class GradientButton(QPushButton):
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(parent)
        self.setObjectName("gradientButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = None
        if icon_name:
            self.icon = IconGlyph(icon_name, size=16)
            self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(self.icon)

        self.text_label = QLabel(text)
        self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self.text_label)

        self.apply_theme()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        if self.icon:
            self.icon.setColor("#FFFFFF")
        self.text_label.setStyleSheet(
            "color:#FFFFFF; background:transparent; border:none; font-size:12px; font-weight:700;"
        )
        self.setStyleSheet(
            f"""
            QPushButton#gradientButton {{
                background:qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {c.PRIMARY_LIGHT},
                    stop:1 {c.PRIMARY}
                );
                border:1px solid rgba(130,165,255,0.52);
                border-radius:{Metrics.CONTROL_RADIUS}px;
            }}
            QPushButton#gradientButton:hover {{
                border-color:rgba(190,210,255,0.85);
            }}
            QPushButton#gradientButton:pressed {{
                background:{c.PRIMARY};
            }}
            """
        )


class AccentOrb(QWidget):
    """Small painted Flux orb used in sidebar/header; no image assets required."""

    def __init__(self, diameter=40, parent=None):
        super().__init__(parent)
        self.setFixedSize(diameter, diameter)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        gradient = QLinearGradient(0, self.height(), self.width(), 0)
        gradient.setColorAt(0.00, QColor("#7A5CFF"))
        gradient.setColorAt(0.48, QColor("#4F7CFF"))
        gradient.setColorAt(1.00, QColor("#55C8FF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))


def clear_layout(layout, keep_stretch=False):
    """Delete widgets/layouts deterministically without leaking stale rows."""
    stop_at = 1 if keep_stretch else 0
    while layout.count() > stop_at:
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget:
            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
        elif child_layout:
            clear_layout(child_layout)
