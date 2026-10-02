from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from themes.manager import ThemeManager
from ui.branding import FluxLogo
from ui.icons import IconGlyph


class SidebarButton(QPushButton):

    activated = Signal(str)

    def __init__(self, icon_name, text, key, parent=None):

        super().__init__(parent)

        self.key = key
        self.active = False

        self.setObjectName("sidebarButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 0, 14, 0)
        row.setSpacing(13)

        self.icon = IconGlyph(icon_name, size=20, stroke_width=1.8)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.label = QLabel(text)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        row.addWidget(self.icon)
        row.addWidget(self.label, 1)

        self.clicked.connect(lambda: self.activated.emit(self.key))

        self.apply_theme()


    def set_active(self, active):

        self.active = bool(active)
        self.apply_theme()


    def apply_theme(self):

        theme = ThemeManager.get()

        if self.active:
            bg = "rgba(80,130,255,0.20)"
            border = theme.Colors.PRIMARY
            text = theme.Colors.TEXT
            icon = theme.Colors.PRIMARY
        else:
            bg = "transparent"
            border = "transparent"
            text = theme.Colors.TEXT_SECONDARY
            icon = theme.Colors.TEXT_SECONDARY

        self.setStyleSheet(
            f"""
            QPushButton#sidebarButton {{
                background:{bg};
                border:none;
                border-left:3px solid {border};
                border-radius:10px;
                text-align:left;
            }}
            QPushButton#sidebarButton:hover {{
                background:rgba(80,130,255,0.11);
                border-left:3px solid {theme.Colors.PRIMARY};
            }}
            """
        )

        self.label.setStyleSheet(
            f"""
            color:{text};
            background:transparent;
            border:none;
            font-size:14px;
            font-weight:{700 if self.active else 520};
            """
        )

        self.icon.setColor(icon)


class Sidebar(QFrame):

    filterChanged = Signal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setObjectName("sidebar")
        self.setFixedWidth(230)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 24, 16, 22)
        root.setSpacing(7)

        self.logo = FluxLogo(
            width=126,
            variant="light" if ThemeManager.current_name == "light" else "dark"
        )

        root.addWidget(
            self.logo,
            0,
            Qt.AlignmentFlag.AlignHCenter
        )

        root.addSpacing(28)

        self.buttons = {}
        self.button_order = []

        items = (
            ("home", "Dashboard", "Dashboard"),
            ("tasks", "Tasks", "Tasks"),
            ("calendar", "Calendar", "Calendar"),
            ("notebook", "Notes", "Notes"),
            ("timer", "Focus", "Focus"),
            ("chart", "Statistics", "Statistics"),
            ("star", "Milestones", "Milestones"),
        )

        for icon_name, text, key in items:

            button = SidebarButton(icon_name, text, key, self)
            button.activated.connect(self.filterChanged.emit)

            self.buttons[key] = button
            self.button_order.append(button)

            root.addWidget(button)

        root.addStretch(1)

        self.divider = QFrame()
        self.divider.setFixedHeight(1)

        root.addWidget(self.divider)

        settings = SidebarButton("gear", "Settings", "Settings", self)
        settings.activated.connect(self.filterChanged.emit)

        self.buttons["Settings"] = settings
        self.button_order.append(settings)

        root.addWidget(settings)

        self.apply_theme()


    def set_active(self, key):

        for button_key, button in self.buttons.items():
            button.set_active(button_key == key)


    def apply_theme(self):

        theme = ThemeManager.get()

        self.setStyleSheet(
            f"""
            QFrame#sidebar {{
                background:{theme.Colors.SECONDARY};
                border:none;
                border-right:1px solid {theme.Colors.BORDER};
                border-top-left-radius:18px;
                border-bottom-left-radius:18px;
            }}
            """
        )

        self.divider.setStyleSheet(
            f"background:{theme.Colors.BORDER}; border:none;"
        )

        for button in self.button_order:
            button.apply_theme()
