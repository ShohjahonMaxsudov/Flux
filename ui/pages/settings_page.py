from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox
)

from utils.settings_manager import SettingsManager
from utils.glass_effects import GlassFrame
from ui.icons import IconGlyph
from themes.manager import ThemeManager

class SettingsPage(QWidget):

    # Emitted when the user's name is saved, so app.py can push it into
    # the Header's greeting immediately instead of waiting for restart.
    nameChanged = Signal(str)


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

        root.addWidget(self.profileCard)



        # APPEARANCE

        self.appearanceCard = GlassFrame()

        self.appearanceCard.setObjectName("appearanceCard")

        self.appearanceCard.glass_radius = 20

        appearanceLayout = QVBoxLayout(self.appearanceCard)

        appearanceLayout.setContentsMargins(24, 22, 24, 22)

        appearanceLayout.setSpacing(12)


        self.appearanceHeading = QLabel("Appearance")

        themeRow = QHBoxLayout()

        themeRow.setSpacing(10)

        self.themeButtons = {}

        self.themeIcons = {}

        for key, icon_name, label in (
            ("dark", "moon", "Dark"),
            ("light", "sun", "Light"),
            ("sakura", "blossom", "Sakura")
        ):

            btn = QPushButton("")

            btn.setCheckable(True)

            btn.setMinimumHeight(40)

            btnLayout = QHBoxLayout(btn)

            btnLayout.setContentsMargins(14, 0, 14, 0)

            btnLayout.setSpacing(8)

            btnLayout.setAlignment(Qt.AlignCenter)

            glyph = IconGlyph(icon_name, size=16, color="white", stroke_width=1.7)

            glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            textLabel = QLabel(label)

            textLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            textLabel.setStyleSheet("background:transparent; border:none; font-weight:600;")

            btnLayout.addWidget(glyph)

            btnLayout.addWidget(textLabel)

            btn.clicked.connect(
                lambda checked, k=key: self.select_theme(k)
            )

            self.themeButtons[key] = btn

            self.themeIcons[key] = glyph

            themeRow.addWidget(btn)

        appearanceLayout.addWidget(self.appearanceHeading)

        appearanceLayout.addLayout(themeRow)

        root.addWidget(self.appearanceCard)



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

        startupLayout.addWidget(self.startupHeading)

        startupLayout.addWidget(self.lockToggle)

        startupLayout.addWidget(self.lockNote)

        root.addWidget(self.startupCard)


        root.addStretch()


        self.apply_theme()



    def save_name(self):

        name = self.nameInput.text().strip()

        self.settings_manager.set_user_name(name)

        self.nameChanged.emit(name)



    def select_theme(self, key):

        ThemeManager.set_theme(key)

        self.settings_manager.set_theme(key)

        self.sync_theme_buttons()



    def sync_theme_buttons(self):

        for key, btn in self.themeButtons.items():

            btn.setChecked(
                key == ThemeManager.current_name
            )

            self.themeIcons[key].setColor(
                "white"
                if key == ThemeManager.current_name
                else ThemeManager.get().Colors.TEXT
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


        for key, btn in self.themeButtons.items():

            btn.setStyleSheet(
                f"""
                QPushButton{{

                    background:{theme.Colors.SURFACE_ALT};

                    color:{theme.Colors.TEXT};

                    border:1px solid {theme.Colors.BORDER};

                    border-radius:12px;

                    padding:10px 16px;

                }}

                QPushButton:checked{{

                    background:{theme.Colors.PRIMARY};

                    color:white;

                    border:1px solid {theme.Colors.PRIMARY};

                }}
                """
            )

        self.sync_theme_buttons()


        self.lockToggle.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:14px; background:transparent; border:none;"
        )

        self.lockNote.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:12px; background:transparent; border:none;"
        )



    def refresh_theme(self):

        self.apply_theme()



    def showEvent(self, event):

        super().showEvent(event)

        self.sync_theme_buttons()
