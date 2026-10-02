from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.design_system import Metrics, SurfaceCard
from utils.settings_manager import SettingsManager


class SettingsPage(QWidget):
    nameChanged = Signal(str)
    reduceMotionChanged = Signal(bool)
    weeklyGoalChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(Metrics.PAGE_X, Metrics.PAGE_Y, Metrics.PAGE_X, Metrics.PAGE_Y)
        outer.setSpacing(16)

        self.title = QLabel("Settings")
        self.title.setObjectName("settingsTitle")
        self.subtitle = QLabel("Keep Flux focused on the way you work.")
        self.subtitle.setObjectName("settingsSubtitle")
        outer.addWidget(self.title)
        outer.addWidget(self.subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} QScrollArea>QWidget>QWidget{background:transparent;}")

        host = QWidget()
        host.setStyleSheet("background:transparent;")
        content = QVBoxLayout(host)
        content.setContentsMargins(0, 0, 6, 0)
        content.setSpacing(14)

        self.profile_card = SurfaceCard("Profile", "Used only to personalize your greeting.")
        profile_row = QHBoxLayout()
        profile_row.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setObjectName("settingsInput")
        self.name_input.setPlaceholderText("What should Flux call you?")
        self.name_input.setText(self.settings_manager.get_user_name())
        self.name_input.returnPressed.connect(self.save_name)
        self.save_name_button = QPushButton("Save")
        self.save_name_button.setObjectName("settingsPrimary")
        self.save_name_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_name_button.clicked.connect(self.save_name)
        profile_row.addWidget(self.name_input, 1)
        profile_row.addWidget(self.save_name_button)
        self.profile_card.body.addLayout(profile_row)
        content.addWidget(self.profile_card)

        self.productivity_card = SurfaceCard("Productivity", "Set the goals used by your Dashboard progress.")

        task_goal_row = self._setting_row(
            "Weekly task goal",
            "How many completed tasks should count as a full week?",
        )
        self.goal_spin = QSpinBox()
        self.goal_spin.setObjectName("settingsSpin")
        self.goal_spin.setRange(1, 200)
        self.goal_spin.setValue(int(self.settings_manager.get("weekly_goal", "18") or 18))
        self.goal_spin.valueChanged.connect(self.on_weekly_goal_changed)
        task_goal_row["row"].addWidget(self.goal_spin)
        self.productivity_card.body.addWidget(task_goal_row["frame"])

        focus_goal_row = self._setting_row(
            "Weekly focus goal",
            "Used by the Focus progress ring on Dashboard.",
        )
        self.focus_goal_spin = QSpinBox()
        self.focus_goal_spin.setObjectName("settingsSpin")
        self.focus_goal_spin.setRange(1, 80)
        stored_minutes = int(self.settings_manager.get("focus_weekly_goal_minutes", "1500") or 1500)
        self.focus_goal_spin.setValue(max(1, round(stored_minutes / 60)))
        self.focus_goal_spin.setSuffix(" h")
        self.focus_goal_spin.valueChanged.connect(self.on_focus_goal_changed)
        focus_goal_row["row"].addWidget(self.focus_goal_spin)
        self.productivity_card.body.addWidget(focus_goal_row["frame"])

        content.addWidget(self.productivity_card)

        self.startup_card = SurfaceCard("Startup", "Small behavior preferences — no skins, no theme gallery.")
        lock_row = self._setting_row(
            "Lock screen on launch",
            "Show Flux's lock screen before the workspace opens.",
        )
        self.lock_toggle = QCheckBox()
        self.lock_toggle.setObjectName("settingsToggle")
        self.lock_toggle.setChecked(self.settings_manager.get_lock_screen_enabled())
        self.lock_toggle.toggled.connect(self.settings_manager.set_lock_screen_enabled)
        lock_row["row"].addWidget(self.lock_toggle)
        self.startup_card.body.addWidget(lock_row["frame"])

        content.addWidget(self.startup_card)

        self.about_card = SurfaceCard("Flux interface", "One visual identity, intentionally.")
        about = QLabel(
            "Flux v3 uses a single Midnight design system so every screen shares the same "
            "spacing, surfaces, controls and hierarchy. Appearance presets were removed."
        )
        about.setObjectName("settingsBody")
        about.setWordWrap(True)
        self.about_card.body.addWidget(about)
        content.addWidget(self.about_card)

        content.addStretch(1)
        scroll.setWidget(host)
        outer.addWidget(scroll, 1)

        self.apply_theme()

    def _setting_row(self, title, description):
        frame = QFrame()
        frame.setObjectName("settingsRow")
        row = QHBoxLayout(frame)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(12)

        text = QVBoxLayout()
        text.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("settingsRowTitle")
        description_label = QLabel(description)
        description_label.setObjectName("settingsRowDescription")
        description_label.setWordWrap(True)
        text.addWidget(title_label)
        text.addWidget(description_label)
        row.addLayout(text, 1)
        return {"frame": frame, "row": row}

    def save_name(self):
        name = self.name_input.text().strip()
        self.settings_manager.set_user_name(name)
        self.nameChanged.emit(name)

    def on_weekly_goal_changed(self, value):
        self.settings_manager.set("weekly_goal", str(value))
        self.weeklyGoalChanged.emit(value)

    def on_focus_goal_changed(self, hours):
        self.settings_manager.set("focus_weekly_goal_minutes", str(int(hours) * 60))

    def apply_theme(self):
        c = ThemeManager.get().Colors
        for card in (self.profile_card, self.productivity_card, self.startup_card, self.about_card):
            card.apply_theme()

        self.setStyleSheet(
            f"""
            QLabel#settingsTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:28px; font-weight:800; }}
            QLabel#settingsSubtitle {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:12px; }}
            QFrame#settingsRow {{ background:{c.SURFACE_ALT}; border:1px solid {c.BORDER}; border-radius:12px; }}
            QLabel#settingsRowTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:12px; font-weight:700; }}
            QLabel#settingsRowDescription, QLabel#settingsBody {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px; }}
            QLineEdit#settingsInput, QSpinBox#settingsSpin {{ color:{c.TEXT}; background:{c.SURFACE_ALT}; border:1px solid {c.BORDER}; border-radius:10px; padding:9px 11px; }}
            QLineEdit#settingsInput:focus, QSpinBox#settingsSpin:focus {{ border-color:{c.BORDER_ACTIVE}; }}
            QPushButton#settingsPrimary {{ color:white; background:{c.PRIMARY}; border:none; border-radius:10px; padding:9px 18px; font-weight:700; }}
            QCheckBox#settingsToggle {{ color:{c.TEXT}; background:transparent; border:none; }}
            QCheckBox#settingsToggle::indicator {{ width:34px; height:18px; border-radius:9px; background:#263244; border:1px solid #394A62; }}
            QCheckBox#settingsToggle::indicator:checked {{ background:{c.PRIMARY}; border-color:{c.PRIMARY_LIGHT}; }}
            """
        )

    def refresh_theme(self):
        self.apply_theme()
