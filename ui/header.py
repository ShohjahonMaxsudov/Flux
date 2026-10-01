from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QApplication
)

from datetime import datetime

from themes.manager import ThemeManager
from utils.color_utils import lighten, rgba
from utils.glass_effects import RefractiveGlassMixin, apply_soft_shadow, apply_glow
from utils.settings_manager import SettingsManager
from ui.icons import IconGlyph


class GlassIconButton(RefractiveGlassMixin, QPushButton):

    # 48x48 icon buttons (Add Task, theme toggle, lock) styled with
    # border-radius:15px in their own stylesheets — glass_radius below
    # has to match that or the highlight won't trace the visible edge.

    glass_radius = 15


    def set_icon_glyph(self, name, color="white", size=20):

        # A hand-drawn vector icon in place of the button's own text —
        # several emoji used before (🌙 🌸 🔒) live outside the Basic
        # Multilingual Plane and don't render reliably without a
        # dedicated color-emoji font, which a bundled build doesn't
        # always have. See ui/icons.py.

        if self.layout() is None:

            layout = QHBoxLayout(self)

            layout.setContentsMargins(0, 0, 0, 0)

            layout.setAlignment(Qt.AlignCenter)

        else:

            layout = self.layout()

            while layout.count():

                item = layout.takeAt(0)

                widget = item.widget()

                if widget:

                    widget.deleteLater()


        self.setText("")

        glyph = IconGlyph(name, size=size, color=color, stroke_width=2.0)

        glyph.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        layout.addWidget(glyph)

        self._iconGlyph = glyph


    def set_icon_color(self, color):

        if hasattr(self, "_iconGlyph"):

            self._iconGlyph.setColor(color)


class Header(QFrame):

    addTaskClicked = Signal()

    lockClicked = Signal()


    def __init__(self):

        super().__init__()

        self.userName = ""

        self.setFixedHeight(120)

        self.build_ui()

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_time
        )

        self.timer.start(
            1000
        )

        self.update_time()



    def build_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            20,
            10,
            20,
            10
        )


        left = QVBoxLayout()

        left.setSpacing(
            3
        )


        self.greeting = QLabel()

        self.subtitle = QLabel()

        self.dateLabel = QLabel()


        left.addWidget(
            self.greeting
        )

        left.addWidget(
            self.subtitle
        )

        left.addWidget(
            self.dateLabel
        )


        layout.addLayout(
            left
        )


        layout.addStretch()



        self.addButton = GlassIconButton(
            "+"
        )


        self.addButton.setFixedSize(
            48,
            48
        )


        self.addButton.setCursor(
            Qt.PointingHandCursor
        )


        apply_soft_shadow(
            self.addButton,
            blur=24,
            y_offset=6,
            alpha=90
        )


        self.addButton.clicked.connect(
            self.addTaskClicked.emit
        )



        self.themeButton = GlassIconButton(
            ""
        )

        self.themeButton.set_icon_glyph(
            "moon"
        )


        self.themeButton.setFixedSize(
            48,
            48
        )


        self.themeButton.setCursor(
            Qt.PointingHandCursor
        )


        apply_soft_shadow(
            self.themeButton,
            blur=24,
            y_offset=6,
            alpha=90
        )


        self.themeButton.clicked.connect(
            self.change_theme
        )


        self.lockButton = GlassIconButton(
            ""
        )

        self.lockButton.set_icon_glyph(
            "lock"
        )


        self.lockButton.setFixedSize(
            48,
            48
        )


        self.lockButton.setCursor(
            Qt.PointingHandCursor
        )


        apply_soft_shadow(
            self.lockButton,
            blur=24,
            y_offset=6,
            alpha=90
        )


        self.lockButton.clicked.connect(
            self.lockClicked.emit
        )

        self.lockButton.setToolTip(
            "Lock Flux"
        )


        # Live clock pill (hh:mm:ss) to the left of the buttons.

        self.clockPill = QFrame()

        self.clockPill.setObjectName("clockPill")

        self.clockPill.setFixedHeight(48)

        pillLayout = QHBoxLayout(self.clockPill)

        pillLayout.setContentsMargins(16, 0, 18, 0)

        pillLayout.setSpacing(9)

        self.clockIcon = IconGlyph(
            "clock",
            size=17,
            color="white",
            stroke_width=1.8
        )

        self.clockLabel = QLabel("00:00:00")

        pillLayout.addWidget(self.clockIcon)

        pillLayout.addWidget(self.clockLabel)

        layout.addWidget(
            self.clockPill
        )

        layout.addSpacing(6)

        layout.addWidget(
            self.addButton
        )


        layout.addWidget(
            self.themeButton
        )


        layout.addWidget(
            self.lockButton
        )


        self.apply_theme()



    def apply_theme(self):

        # Always get fresh theme
        theme = ThemeManager.get()


        self.setStyleSheet(
            """
            QFrame {
                background: transparent;
                border: none;
            }
            """
        )


        self.greeting.setStyleSheet(
            f"""
            QLabel {{
                color:{theme.Colors.TEXT};
                font-size:28px;
                font-weight:700;
                background:transparent;
                border:none;
            }}
            """
        )


        self.subtitle.setStyleSheet(
            f"""
            QLabel {{
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:14px;
                background:transparent;
                border:none;
            }}
            """
        )


        self.dateLabel.setStyleSheet(
            f"""
            QLabel {{
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:12px;
                background:transparent;
                border:none;
            }}
            """
        )



        glow = ThemeManager.style().GLOW

        if glow > 0:

            # Glass primary: light-to-deep accent gradient, a thin bright
            # rim, and a coloured halo instead of a black shadow.

            top = lighten(theme.Colors.PRIMARY, 122)

            self.addButton.setStyleSheet(
                f"""
                QPushButton {{
                    background:qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {top}, stop:1 {theme.Colors.PRIMARY});
                    color:white;
                    border-radius:15px;
                    font-size:28px;
                    border:1px solid {rgba("#FFFFFF", 0.30)};
                }}

                QPushButton:hover {{
                    background:qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {lighten(top, 110)}, stop:1 {lighten(theme.Colors.PRIMARY, 112)});
                }}

                QPushButton:pressed {{
                    background:{theme.Colors.PRIMARY};
                }}
                """
            )

            apply_glow(
                self.addButton,
                theme.Colors.PRIMARY,
                blur=32,
                y_offset=6,
                alpha=int(230 * glow)
            )

        else:

            self.addButton.setStyleSheet(
                f"""
                QPushButton {{
                    background:{theme.Colors.PRIMARY};
                    color:{theme.Colors.TEXT};
                    border-radius:15px;
                    font-size:28px;
                    border:none;
                }}

                QPushButton:hover {{
                    background:{theme.Colors.BORDER_ACTIVE};
                }}

                QPushButton:pressed {{
                    background:{theme.Colors.GLASS_HOVER};
                }}
                """
            )

            apply_glow(
                self.addButton,
                QColor(0, 0, 0),
                blur=24,
                y_offset=6,
                alpha=90
            )



        self.themeButton.setStyleSheet(
            f"""
            QPushButton {{
                background:{theme.Colors.GLASS};
                color:{theme.Colors.TEXT};
                border-radius:15px;
                font-size:20px;
                border:1px solid {theme.Colors.BORDER};
            }}

            QPushButton:hover {{
                background:{theme.Colors.GLASS_HOVER};
            }}

            QPushButton:pressed {{
                background:{theme.Colors.SURFACE_ALT};
            }}
            """
        )



        self.lockButton.setStyleSheet(
            f"""
            QPushButton {{
                background:{theme.Colors.GLASS};
                color:{theme.Colors.TEXT};
                border-radius:15px;
                font-size:18px;
                border:1px solid {theme.Colors.BORDER};
            }}

            QPushButton:hover {{
                background:{theme.Colors.GLASS_HOVER};
            }}

            QPushButton:pressed {{
                background:{theme.Colors.SURFACE_ALT};
            }}
            """
        )

        # The glass buttons' glyphs used to be hardcoded white, which
        # vanished on the Light theme; follow the theme's text colour.

        self.themeButton.set_icon_color(theme.Colors.TEXT)

        self.lockButton.set_icon_color(theme.Colors.TEXT)

        # The theme button shows the *current* theme's glyph (it used to
        # always start on the moon, even when a saved theme was loaded).

        self.themeButton.set_icon_glyph(
            ThemeManager.icon(ThemeManager.current_name)
        )

        self.themeButton.set_icon_color(theme.Colors.TEXT)

        self.clockPill.setStyleSheet(
            f"""
            QFrame#clockPill {{
                background:{theme.Colors.GLASS};
                border:1px solid {theme.Colors.BORDER};
                border-radius:15px;
            }}
            """
        )

        self.clockIcon.setColor(
            lighten(theme.Colors.PRIMARY, 125)
            if ThemeManager.style().GLOW > 0
            else theme.Colors.TEXT_SECONDARY
        )

        self.clockLabel.setStyleSheet(
            f"""
            QLabel {{
                color:{theme.Colors.TEXT};
                font-size:14px;
                font-weight:600;
                background:transparent;
                border:none;
            }}
            """
        )




    def change_theme(self):

        next_theme = ThemeManager.next_name()

        ThemeManager.set_theme(
            next_theme
        )

        settings = SettingsManager()

        settings.set_theme(
            next_theme
        )

        settings.close()

        # (The app-wide stylesheet is re-applied once by the main window's
        # theme-changed handler.)
        #
        # Also re-runs apply_theme() via the theme-changed broadcast, but
        # the header must never be left stale if that broadcast is
        # missing, so refresh directly too (this also swaps the button's
        # glyph to the new theme's icon).

        self.apply_theme()



    def set_user_name(self, name):

        self.userName = (name or "").strip()

        self.update_time()



    def update_time(self):

        now = datetime.now()

        hour = now.hour


        if hour < 12:

            greeting = "Good Morning ☀︎"

            subtitle = "Ready to start the day?"


        elif hour < 18:

            greeting = "Good Afternoon ⛅︎"

            subtitle = "Keep the momentum going."


        else:

            greeting = "Good Evening ☾︎"

            subtitle = "Finish strong today."


        if self.userName:

            # Split the trailing emoji off so a name inserts naturally:
            # "Good Morning, Ian ☀️" rather than "Good Morning ☀️, Ian".
            words = greeting.rsplit(" ", 1)

            greeting = f"{words[0]}, {self.userName} {words[1]}"



        self.clockLabel.setText(
            now.strftime("%H:%M:%S")
        )

        self.greeting.setText(
            greeting
        )


        self.subtitle.setText(
            subtitle
        )


        self.dateLabel.setText(
            now.strftime(
                "%A, %B %d"
            )
        )