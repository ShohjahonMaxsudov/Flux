from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from themes.manager import ThemeManager
from ui.design_system import AccentOrb, Metrics
from ui.icons import IconGlyph


class NavButton(QPushButton):
    activated = Signal(str)

    def __init__(self, icon_name, label, key, parent=None):
        super().__init__(parent)
        self.key = key
        self.active = False
        self.setObjectName("navButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(46)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(12)

        self.icon = IconGlyph(icon_name, size=20, stroke_width=1.8)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.label = QLabel(label)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        row.addWidget(self.icon)
        row.addWidget(self.label, 1)

        self.clicked.connect(lambda: self.activated.emit(self.key))
        self.apply_theme()

    def set_active(self, active):
        self.active = bool(active)
        self.apply_theme()

    def apply_theme(self):
        c = ThemeManager.get().Colors

        if self.active:
            bg = "rgba(76,116,220,0.28)"
            edge = c.BLUE_SOFT
            text = c.TEXT
            icon = c.BLUE_SOFT
        else:
            bg = "transparent"
            edge = "transparent"
            text = c.TEXT_SECONDARY
            icon = "#9BB0D4"

        self.setStyleSheet(
            f"""
            QPushButton#navButton {{
                background:{bg};
                border:none;
                border-left:2px solid {edge};
                border-radius:9px;
            }}
            QPushButton#navButton:hover {{
                background:rgba(68,94,140,0.20);
                border-left:2px solid {c.BLUE_SOFT};
            }}
            """
        )
        self.icon.setColor(icon)
        self.label.setStyleSheet(
            f"color:{text}; background:transparent; border:none; font-size:13px; font-weight:{700 if self.active else 500};"
        )


class Sidebar(QFrame):
    filterChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fluxSidebar")
        self.setFixedWidth(Metrics.SIDEBAR_WIDTH)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 12, 16)
        root.setSpacing(6)

        traffic = QHBoxLayout()
        traffic.setSpacing(7)
        traffic.setContentsMargins(3, 1, 0, 0)
        for color in ("#FF625F", "#F7BE4F", "#2ACB58"):
            dot = QFrame()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"background:{color}; border:none; border-radius:6px;")
            traffic.addWidget(dot)
        traffic.addStretch(1)
        root.addLayout(traffic)
        root.addSpacing(18)

        brand = QHBoxLayout()
        brand.setContentsMargins(6, 0, 0, 0)
        brand.setSpacing(12)

        self.orb = AccentOrb(36)
        self.brand_name = QLabel("Flux")
        self.brand_name.setObjectName("brandName")

        brand.addWidget(self.orb)
        brand.addWidget(self.brand_name)
        brand.addStretch(1)
        root.addLayout(brand)

        root.addSpacing(28)

        self.buttons = {}
        self._button_list = []

        items = (
            ("home", "Dashboard", "Dashboard"),
            ("tasks", "Tasks", "Tasks"),
            ("calendar", "Calendar", "Calendar"),
            ("notebook", "Notes", "Notes"),
            ("timer", "Focus", "Focus"),
            ("chart", "Statistics", "Statistics"),
            ("star", "Milestones", "Milestones"),
        )

        for icon_name, label, key in items:
            button = NavButton(icon_name, label, key, self)
            button.activated.connect(self.filterChanged.emit)
            self.buttons[key] = button
            self._button_list.append(button)
            root.addWidget(button)

        root.addStretch(1)

        self.divider = QFrame()
        self.divider.setFixedHeight(1)
        root.addWidget(self.divider)
        root.addSpacing(3)

        settings = NavButton("gear", "Settings", "Settings", self)
        settings.activated.connect(self.filterChanged.emit)
        self.buttons["Settings"] = settings
        self._button_list.append(settings)
        root.addWidget(settings)

        self.apply_theme()

    def set_active(self, key):
        for button_key, button in self.buttons.items():
            button.set_active(button_key == key)

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.setStyleSheet(
            f"""
            QFrame#fluxSidebar {{
                background:{c.SECONDARY};
                border:none;
                border-right:1px solid {c.BORDER};
                border-top-left-radius:18px;
                border-bottom-left-radius:18px;
            }}
            QLabel#brandName {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:24px;
                font-weight:800;
            }}
            """
        )
        self.divider.setStyleSheet(f"background:{c.BORDER}; border:none;")
        for button in self._button_list:
            button.apply_theme()
