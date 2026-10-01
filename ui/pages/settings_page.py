from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QColorDialog,
    QSlider,
    QSpinBox,
    QScrollArea,
    QFrame
)

from utils.settings_manager import SettingsManager
from utils.glass_effects import GlassFrame
from ui.icons import IconGlyph
from ui.branding import CreditsFooter
from ui.theme_picker import ThemePicker
from themes.manager import ThemeManager
from themes.custom_state import CustomState

class SettingsPage(QWidget):

    # Emitted when the user's name is saved, so app.py can push it into
    # the Header's greeting immediately instead of waiting for restart.
    nameChanged = Signal(str)

    # Emitted when the "reduce background motion" toggle changes, so
    # app.py can start/stop the animated backgrounds immediately.
    reduceMotionChanged = Signal(bool)

    # Emitted when the weekly task goal changes, so the Dashboard's
    # Weekly Progress ring updates immediately instead of waiting for
    # the next task to be added or completed.
    weeklyGoalChanged = Signal(int)


    def __init__(self):

        super().__init__()

        self.settings_manager = SettingsManager()


        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(18)


        self.title = QLabel("Settings")

        self.subtitle = QLabel("Make Flux feel like yours.")

        root.addWidget(self.title)

        root.addWidget(self.subtitle)


        # The page grew past one screen once Custom joined the theme
        # grid and Startup picked up the motion/goal controls — scroll
        # the cards instead of letting them get squeezed to fit.

        self.contentHost = QWidget()

        content = QVBoxLayout(self.contentHost)

        content.setContentsMargins(0, 0, 6, 0)

        content.setSpacing(18)

        self.contentScroll = QScrollArea()

        self.contentScroll.setWidgetResizable(True)

        self.contentScroll.setFrameShape(QFrame.Shape.NoFrame)

        self.contentScroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.contentScroll.setWidget(self.contentHost)

        root.addWidget(self.contentScroll, 1)



        # PROFILE

        self.profileCard = GlassFrame()

        self.profileCard.setObjectName("profileCard")

        self.profileCard.glass_radius = 20

        profileLayout = QVBoxLayout(self.profileCard)

        profileLayout.setContentsMargins(24, 22, 24, 22)

        profileLayout.setSpacing(12)


        self.profileHeading = QLabel("Profile")

        self.nameLabel = QLabel("Your Name")

        row = QHBoxLayout()

        self.nameInput = QLineEdit()

        self.nameInput.setPlaceholderText("What should Flux call you?")

        self.nameInput.setText(
            self.settings_manager.get_user_name()
        )

        self.nameInput.returnPressed.connect(
            self.save_name
        )

        self.saveNameButton = QPushButton("Save")

        self.saveNameButton.clicked.connect(
            self.save_name
        )

        row.addWidget(self.nameInput, 1)

        row.addWidget(self.saveNameButton)

        profileLayout.addWidget(self.profileHeading)

        profileLayout.addWidget(self.nameLabel)

        profileLayout.addLayout(row)

        content.addWidget(self.profileCard)



        # APPEARANCE

        self.appearanceCard = GlassFrame()

        self.appearanceCard.setObjectName("appearanceCard")

        self.appearanceCard.glass_radius = 20

        appearanceLayout = QVBoxLayout(self.appearanceCard)

        appearanceLayout.setContentsMargins(24, 22, 24, 22)

        appearanceLayout.setSpacing(12)


        self.appearanceHeading = QLabel("Appearance")

        # One card per theme, each a live miniature of that theme.

        self.themePicker = ThemePicker()

        self.themePicker.themeSelected.connect(
            self.select_theme
        )

        appearanceLayout.addWidget(self.appearanceHeading)

        appearanceLayout.addWidget(self.themePicker)


        # The Custom tile above is selected the same way as any other
        # theme; these two controls are what actually shape it — tap
        # the swatch to pick a primary color, drag the slider for how
        # much glow/aurora the theme carries. Both apply live.

        customizeRow = QHBoxLayout()

        customizeRow.setSpacing(10)

        self.customizeLabel = QLabel("Custom theme")

        self.colorSwatch = QPushButton()

        self.colorSwatch.setFixedSize(28, 28)

        self.colorSwatch.setCursor(Qt.CursorShape.PointingHandCursor)

        self.colorSwatch.setToolTip("Choose the Custom theme's primary color")

        self.colorSwatch.clicked.connect(self.pick_custom_color)

        self.glowLabel = QLabel("Glow")

        self.glowSlider = QSlider(Qt.Orientation.Horizontal)

        self.glowSlider.setRange(0, 100)

        self.glowSlider.setFixedWidth(140)

        self.glowSlider.setCursor(Qt.CursorShape.PointingHandCursor)

        self.glowSlider.valueChanged.connect(self.on_glow_dragging)

        self.glowSlider.sliderReleased.connect(self.on_glow_released)

        customizeRow.addWidget(self.customizeLabel)

        customizeRow.addSpacing(6)

        customizeRow.addWidget(self.colorSwatch)

        customizeRow.addSpacing(20)

        customizeRow.addWidget(self.glowLabel)

        customizeRow.addWidget(self.glowSlider)

        customizeRow.addStretch()

        appearanceLayout.addLayout(customizeRow)

        content.addWidget(self.appearanceCard)



        # STARTUP

        self.startupCard = GlassFrame()

        self.startupCard.setObjectName("startupCard")

        self.startupCard.glass_radius = 20

        startupLayout = QVBoxLayout(self.startupCard)

        startupLayout.setContentsMargins(24, 22, 24, 22)

        startupLayout.setSpacing(12)


        self.startupHeading = QLabel("Startup")

        self.lockToggle = QCheckBox(
            "Show lock screen when Flux opens"
        )

        self.lockToggle.setChecked(
            self.settings_manager.get_lock_screen_enabled()
        )

        self.lockToggle.toggled.connect(
            self.settings_manager.set_lock_screen_enabled
        )

        self.lockNote = QLabel(
            "Takes effect the next time you open Flux."
        )

        self.motionToggle = QCheckBox(
            "Reduce background motion"
        )

        self.motionToggle.setChecked(
            self.settings_manager.get("reduce_motion", "0") == "1"
        )

        self.motionToggle.toggled.connect(
            self.on_reduce_motion_toggled
        )

        self.motionNote = QLabel(
            "Keeps each theme's look, just holds the animation still."
        )

        goalRow = QHBoxLayout()

        goalRow.setSpacing(10)

        self.goalLabel = QLabel("Weekly task goal")

        self.goalSpin = QSpinBox()

        self.goalSpin.setRange(1, 200)

        self.goalSpin.setValue(
            int(self.settings_manager.get("weekly_goal", "35") or 35)
        )

        self.goalSpin.setFixedWidth(90)

        self.goalSpin.valueChanged.connect(self.on_weekly_goal_changed)

        goalRow.addWidget(self.goalLabel)

        goalRow.addWidget(self.goalSpin)

        goalRow.addStretch()

        startupLayout.addWidget(self.startupHeading)

        startupLayout.addWidget(self.lockToggle)

        startupLayout.addWidget(self.lockNote)

        startupLayout.addWidget(self.motionToggle)

        startupLayout.addWidget(self.motionNote)

        startupLayout.addLayout(goalRow)

        content.addWidget(self.startupCard)


        content.addStretch()


        # Tiny signature strip pinned to the bottom of the page. Purely
        # decorative - it ignores the mouse, so it can't be clicked.

        self.credits = CreditsFooter()

        content.addWidget(self.credits, 0, Qt.AlignHCenter)


        self.apply_theme()



    def save_name(self):

        name = self.nameInput.text().strip()

        self.settings_manager.set_user_name(name)

        self.nameChanged.emit(name)



    def select_theme(self, key):

        ThemeManager.set_theme(key)

        self.settings_manager.set_theme(key)

        self.sync_theme_buttons()


    def on_reduce_motion_toggled(self, enabled):

        self.settings_manager.set("reduce_motion", "1" if enabled else "0")

        self.reduceMotionChanged.emit(enabled)


    def on_weekly_goal_changed(self, value):

        self.settings_manager.set("weekly_goal", str(value))

        self.weeklyGoalChanged.emit(value)


    def pick_custom_color(self):

        initial = QColor(CustomState.get()[0])

        color = QColorDialog.getColor(initial, self, "Choose a primary color")

        if not color.isValid():

            return

        CustomState.set(primary=color.name())

        self.sync_custom_controls()

        self.apply_custom_live()


    def on_glow_dragging(self, value):

        # Persist as the user drags, but don't repaint the whole app on
        # every tick — that happens once, on release (see below).

        CustomState.set(glow=value / 100)


    def on_glow_released(self):

        self.apply_custom_live()


    def apply_custom_live(self):

        if ThemeManager.current_name != "custom":

            self.select_theme("custom")

        else:

            ThemeManager.refresh_current()


    def sync_custom_controls(self):

        primary, glow = CustomState.get()

        self.colorSwatch.setStyleSheet(
            f"background:{primary}; border-radius:14px; border:2px solid white;"
        )

        self.glowSlider.blockSignals(True)

        self.glowSlider.setValue(int(glow * 100))

        self.glowSlider.blockSignals(False)



    def sync_theme_buttons(self):

        self.themePicker.set_current(
            ThemeManager.current_name
        )



    def apply_theme(self):

        theme = ThemeManager.get()


        self.title.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:32px; font-weight:800; background:transparent; border:none;"
        )

        self.subtitle.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:15px; background:transparent; border:none;"
        )


        for card in (self.profileCard, self.appearanceCard, self.startupCard):

            card.setStyleSheet(
                f"""
                QFrame#{card.objectName()}{{

                    background:{theme.Colors.GLASS};

                    border-radius:20px;

                    border:1px solid {theme.Colors.BORDER};

                }}
                """
            )


        for heading in (self.profileHeading, self.appearanceHeading, self.startupHeading):

            heading.setStyleSheet(
                f"color:{theme.Colors.TEXT}; font-size:20px; font-weight:700; background:transparent; border:none;"
            )


        self.nameLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:13px; background:transparent; border:none;"
        )


        self.nameInput.setStyleSheet(
            f"""
            QLineEdit{{

                background:{theme.Colors.SURFACE_ALT};

                color:{theme.Colors.TEXT};

                border:1px solid {theme.Colors.BORDER};

                border-radius:12px;

                padding:10px;

            }}

            QLineEdit:focus{{

                border:1px solid {theme.Colors.PRIMARY};

            }}
            """
        )


        self.saveNameButton.setStyleSheet(
            f"""
            QPushButton{{

                background:{theme.Colors.PRIMARY};

                color:white;

                border-radius:12px;

                padding:10px 20px;

                font-weight:bold;

            }}

            QPushButton:hover{{

                background:{theme.Colors.BORDER_ACTIVE};

            }}
            """
        )


        self.themePicker.refresh()

        self.sync_theme_buttons()

        self.sync_custom_controls()

        self.customizeLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:13px; font-weight:600; background:transparent; border:none;"
        )

        self.glowLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:12px; background:transparent; border:none;"
        )

        self.glowSlider.setStyleSheet(
            f"""
            QSlider::groove:horizontal{{
                height:4px;
                background:{theme.Colors.BORDER};
                border-radius:2px;
            }}
            QSlider::handle:horizontal{{
                background:{theme.Colors.PRIMARY};
                width:14px;
                height:14px;
                margin:-5px 0;
                border-radius:7px;
            }}
            """
        )


        self.lockToggle.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:14px; background:transparent; border:none;"
        )

        self.lockNote.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:12px; background:transparent; border:none;"
        )

        self.motionToggle.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:14px; background:transparent; border:none;"
        )

        self.motionNote.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:12px; background:transparent; border:none;"
        )

        self.goalLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:14px; background:transparent; border:none;"
        )

        self.goalSpin.setStyleSheet(
            f"""
            QSpinBox{{
                color:{theme.Colors.TEXT};
                background:{theme.Colors.SURFACE_ALT};
                border:1px solid {theme.Colors.BORDER};
                border-radius:8px;
                padding:4px 6px;
            }}
            """
        )


        self.credits.set_color(
            theme.Colors.TEXT
        )



    def refresh_theme(self):

        self.apply_theme()



    def showEvent(self, event):

        super().showEvent(event)

        self.sync_theme_buttons()
