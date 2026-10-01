from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)

from themes.manager import ThemeManager
from utils.color_utils import lighten, rgba
from utils.glass_effects import RefractiveGlassMixin, apply_soft_shadow
from ui.progress_ring import ProgressRing
from ui.icons import IconGlyph
from ui.branding import FluxLogo



class SidebarButton(QPushButton):

    clickedFilter = Signal(str)


    def __init__(
        self,
        icon_name,
        text,
        key
    ):

        super().__init__(
            ""
        )

        self.key = key


        self.setCursor(
            Qt.PointingHandCursor
        )


        self.setFixedHeight(
            42
        )


        self.setMinimumWidth(
            190
        )


        # Composited icon + label rather than an emoji baked into the
        # button's own text — see ui/icons.py for why.

        row = QHBoxLayout(self)

        row.setContentsMargins(16, 0, 14, 0)

        row.setSpacing(12)


        self.iconGlyph = IconGlyph(
            icon_name,
            size=18,
            stroke_width=1.8
        )

        self.iconGlyph.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )


        self.textLabel = QLabel(
            text
        )

        self.textLabel.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )


        row.addWidget(
            self.iconGlyph
        )

        row.addWidget(
            self.textLabel
        )

        row.addStretch()


        self.clicked.connect(
            self.emitFilter
        )


        self.anim = QPropertyAnimation(
            self,
            b"geometry"
        )


        self.anim.setDuration(
            180
        )


        self.anim.setEasingCurve(
            QEasingCurve.OutCubic
        )


        self.active = False

        self.apply_theme()



    def apply_theme(self):

        theme = ThemeManager.get()


        glass = ThemeManager.style().NAV_STYLE == "glass"

        icon_color = (
            (lighten(theme.Colors.PRIMARY, 135) if glass else "white")
            if self.active
            else theme.Colors.TEXT_SECONDARY
        )

        self.iconGlyph.setColor(
            icon_color
        )


        if self.active:

            if glass:

                # Tinted glass: a wash of the accent that fades to the
                # right, with a rim - the "selected" state in the concept.

                background = (
                    "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                    f"stop:0 {rgba(theme.Colors.PRIMARY, 0.36)}, "
                    f"stop:1 {rgba(theme.Colors.PRIMARY, 0.10)})"
                )

                border = rgba(theme.Colors.PRIMARY, 0.55)

                text_color = theme.Colors.TEXT

            else:

                background = theme.Colors.PRIMARY

                border = theme.Colors.BORDER_ACTIVE

                text_color = "white"

            self.setStyleSheet(
                f"""
                QPushButton{{

                    background:{background};

                    border-radius:14px;

                    border:1px solid {border};

                }}
                """
            )

            self.textLabel.setStyleSheet(
                f"color:{text_color}; font-size:14px; font-weight:700; background:transparent;"
            )


        else:

            self.setStyleSheet(
                f"""
                QPushButton{{

                    background:transparent;

                    border:none;

                    border-radius:14px;

                }}

                QPushButton:hover{{

                    background:{theme.Colors.GLASS_HOVER};

                }}
                """
            )

            self.textLabel.setStyleSheet(
                f"color:{theme.Colors.TEXT_SECONDARY}; font-size:14px; font-weight:600; background:transparent;"
            )



    def emitFilter(self):

        self.clickedFilter.emit(
            self.key
        )



    def setActive(
        self,
        active
    ):

        self.active = active

        self.apply_theme()





class Sidebar(RefractiveGlassMixin, QFrame):

    glass_radius = 24

    filterChanged = Signal(str)


    def __init__(self):

        super().__init__()


        self.setFixedWidth(
            250
        )


        layout = QVBoxLayout(
            self
        )


        layout.setContentsMargins(
            18,
            22,
            18,
            22
        )


        layout.setSpacing(
            6
        )



        self.logo = FluxLogo(
            width=150,
            variant="light" if ThemeManager.current_name == "light" else "dark"
        )


        self.subtitle = QLabel(
            "Organize Today"
        )

        self.subtitle.setAlignment(
            Qt.AlignHCenter
        )



        layout.addWidget(
            self.logo,
            alignment=Qt.AlignHCenter
        )


        layout.addWidget(
            self.subtitle
        )


        layout.addSpacing(
            24
        )



        self.buttons = []



        items = [

            ("home", "Dashboard", "Dashboard"),

            ("tasks", "Tasks", "Tasks"),

            ("timer", "Focus", "Focus"),

            ("calendar", "Calendar", "Calendar"),

            ("notebook", "Notes", "Notes"),

            ("chart", "Statistics", "Statistics"),

            ("gear", "Settings", "Settings"),

        ]



        for index, (icon_name, text, key) in enumerate(items):


            button = SidebarButton(
                icon_name,
                text,
                key
            )


            if index == 0:

                button.setActive(
                    True
                )


            button.clickedFilter.connect(
                self.changeFilter
            )


            self.buttons.append(
                button
            )


            layout.addWidget(
                button
            )



        layout.addStretch()



        self.progressCard = QFrame()

        self.progressCard.setObjectName(
            "sidebarProgressCard"
        )


        progressLayout = QVBoxLayout(
            self.progressCard
        )

        progressLayout.setAlignment(
            Qt.AlignCenter
        )

        progressLayout.setContentsMargins(
            16, 20, 16, 20
        )

        progressLayout.setSpacing(
            8
        )


        self.progressRing = ProgressRing(
            diameter=100,
            thickness=8
        )


        self.progressTitle = QLabel(
            "Today's Progress"
        )

        self.progressTitle.setAlignment(
            Qt.AlignCenter
        )


        self.progressSubtitle = QLabel(
            "Keep going!"
        )

        self.progressSubtitle.setAlignment(
            Qt.AlignCenter
        )


        progressLayout.addWidget(
            self.progressRing,
            alignment=Qt.AlignCenter
        )

        progressLayout.addWidget(
            self.progressTitle
        )

        progressLayout.addWidget(
            self.progressSubtitle
        )


        layout.addWidget(
            self.progressCard
        )


        self.apply_theme()

        apply_soft_shadow(
            self,
            blur=40,
            y_offset=0,
            alpha=70
        )



    def apply_theme(self):

        theme = ThemeManager.get()



        self.setStyleSheet(
            f"""
            QFrame{{

                background:{theme.Colors.GLASS};

                border-radius:24px;

                border:1px solid {theme.Colors.BORDER};

            }}


            QLabel{{

                background:transparent;

                border:none;

            }}

            """
        )



        # The logo is an image, so it doesn't take a stylesheet; it just
        # needs the right variant for the active theme (white wordmark on
        # dark/sakura, ink wordmark on light).

        self.logo.set_theme(
            ThemeManager.current_name
        )



        self.subtitle.setStyleSheet(
            f"""
            QLabel{{

                color:{theme.Colors.TEXT_SECONDARY};

                font-size:12px;

            }}

            """
        )



        if ThemeManager.style().PANEL_TINT:

            card_background = (
                "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                f"stop:0 {rgba(theme.Colors.PRIMARY, 0.16)}, "
                f"stop:1 {rgba(theme.Colors.PURPLE, 0.07)})"
            )

            card_border = rgba(theme.Colors.PRIMARY, 0.26)

        else:

            card_background = theme.Colors.SURFACE_ALT

            card_border = theme.Colors.BORDER

        self.progressCard.setStyleSheet(
            f"""
            QFrame#sidebarProgressCard{{

                background:{card_background};

                border:1px solid {card_border};

                border-radius:18px;

            }}
            """
        )


        self.progressRing.setColors(
            arc_color=theme.Colors.PRIMARY,
            track_color=QColor(255, 255, 255, 36),
            text_color=theme.Colors.TEXT
        )


        self.progressTitle.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:14px;
            font-weight:700;
            background:transparent;
            border:none;
            """
        )


        self.progressSubtitle.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT_SECONDARY};
            font-size:12px;
            background:transparent;
            border:none;
            """
        )



        for button in self.buttons:

            button.apply_theme()



    def set_progress(self, percent):

        self.progressRing.setValue(percent)



    def changeFilter(
        self,
        key
    ):


        for button in self.buttons:

            button.setActive(
                button.key == key
            )


        self.filterChanged.emit(
            key
        )