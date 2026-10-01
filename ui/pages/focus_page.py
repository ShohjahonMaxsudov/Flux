from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QSpinBox,
)

from utils.focus_manager import FocusManager
from utils.color_utils import rgba, lighten, qcolor
from utils.glass_effects import GlassFrame, apply_soft_shadow, apply_glow
from themes.manager import ThemeManager
from ui.icons import IconGlyph
from ui.progress_ring import ProgressRing
from ui.toast import notify


PRESETS = (
    ("25 / 5", 25, 5),
    ("50 / 10", 50, 10),
)


class _RoundButton(QPushButton):

    # A circular glass icon button — same idea as the header's play/lock
    # buttons, kept local since only this page needs it at this size.

    def __init__(self, icon_name, diameter=52, icon_size=20):

        super().__init__()

        self.setFixedSize(diameter, diameter)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.glyph = IconGlyph(
            icon_name,
            size=icon_size,
            color="white",
            stroke_width=2.0
        )

        layout.addWidget(self.glyph)

    def set_icon(self, icon_name):

        # IconGlyph re-reads self.name on every paint, so swapping the
        # icon is just this — no need to replace the widget.

        self.glyph.name = icon_name

        self.glyph.update()


class FocusPage(QWidget):

    def __init__(self):

        super().__init__()

        self.focus_manager = FocusManager()

        self.focus_minutes = 25

        self.break_minutes = 5

        self.phase = "focus"

        self.total_seconds = self.focus_minutes * 60

        self.remaining_seconds = self.total_seconds

        self.running = False

        self.sessions_today = 0

        self.timer = QTimer(self)

        self.timer.setInterval(1000)

        self.timer.timeout.connect(self._tick)

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(18)

        self.title = QLabel("Focus")

        self.subtitle = QLabel("One session at a time.")

        root.addWidget(self.title)

        root.addWidget(self.subtitle)

        body = QHBoxLayout()

        body.setSpacing(20)

        # ---- timer card --------------------------------------------------

        self.timerCard = GlassFrame()

        self.timerCard.setObjectName("timerCard")

        self.timerCard.glass_radius = 26

        timerLayout = QVBoxLayout(self.timerCard)

        timerLayout.setContentsMargins(30, 30, 30, 30)

        timerLayout.setSpacing(18)

        timerLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.phaseLabel = QLabel("FOCUS SESSION")

        self.phaseLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        timerLayout.addWidget(self.phaseLabel)

        self.ring = ProgressRing(diameter=232, thickness=14)

        timerLayout.addWidget(self.ring, 0, Qt.AlignmentFlag.AlignHCenter)

        controlRow = QHBoxLayout()

        controlRow.setSpacing(16)

        controlRow.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.resetButton = _RoundButton("reset", diameter=48, icon_size=18)

        self.resetButton.clicked.connect(self.reset_timer)

        self.playButton = _RoundButton("play", diameter=64, icon_size=24)

        self.playButton.clicked.connect(self.toggle_running)

        controlRow.addWidget(self.resetButton)

        controlRow.addWidget(self.playButton)

        controlRow.addSpacing(48)

        timerLayout.addLayout(controlRow)

        presetRow = QHBoxLayout()

        presetRow.setSpacing(10)

        presetRow.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.presetButtons = []

        for label, focus_min, break_min in PRESETS:

            button = QPushButton(label)

            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.clicked.connect(
                lambda _checked=False, f=focus_min, b=break_min: self.apply_preset(f, b)
            )

            presetRow.addWidget(button)

            self.presetButtons.append((button, focus_min, break_min))

        self.customSpin = QSpinBox()

        self.customSpin.setRange(5, 180)

        self.customSpin.setValue(25)

        self.customSpin.setSuffix(" min")

        self.customSpin.setFixedWidth(90)

        self.customApply = QPushButton("Custom")

        self.customApply.setCursor(Qt.CursorShape.PointingHandCursor)

        self.customApply.clicked.connect(
            lambda: self.apply_preset(
                self.customSpin.value(),
                max(5, self.customSpin.value() // 5)
            )
        )

        presetRow.addWidget(self.customSpin)

        presetRow.addWidget(self.customApply)

        timerLayout.addLayout(presetRow)

        body.addWidget(self.timerCard, 3)

        # ---- side stats ----------------------------------------------

        sideCol = QVBoxLayout()

        sideCol.setSpacing(16)

        self.todayCard = self._make_stat_card("Today's Focus", "0m")

        self.weekCard = self._make_stat_card("This Week", "0m")

        self.sessionsCard = self._make_stat_card("Sessions Today", "0")

        sideCol.addWidget(self.todayCard)

        sideCol.addWidget(self.weekCard)

        sideCol.addWidget(self.sessionsCard)

        sideCol.addStretch()

        sideWrap = QWidget()

        sideWrap.setLayout(sideCol)

        body.addWidget(sideWrap, 2)

        root.addLayout(body, 1)

        root.addStretch()

        self.apply_theme()

        self._sync_ring()

        self.refresh_stats()

    # -----------------------------------------------------------------
    # small stat card
    # -----------------------------------------------------------------

    def _make_stat_card(self, title, value):

        frame = GlassFrame()

        frame.glass_radius = 18

        layout = QVBoxLayout(frame)

        layout.setContentsMargins(18, 14, 18, 14)

        layout.setSpacing(4)

        title_label = QLabel(title)

        value_label = QLabel(value)

        layout.addWidget(title_label)

        layout.addWidget(value_label)

        frame._titleLabel = title_label

        frame._valueLabel = value_label

        apply_soft_shadow(frame)

        return frame

    # -----------------------------------------------------------------
    # timer mechanics
    # -----------------------------------------------------------------

    def apply_preset(self, focus_minutes, break_minutes):

        self.timer.stop()

        self.running = False

        self.focus_minutes = focus_minutes

        self.break_minutes = break_minutes

        self.phase = "focus"

        self.total_seconds = self.focus_minutes * 60

        self.remaining_seconds = self.total_seconds

        self._sync_ring()

        self._sync_play_icon()

    def reset_timer(self):

        self.apply_preset(self.focus_minutes, self.break_minutes)

    def toggle_running(self):

        self.running = not self.running

        if self.running:

            self.timer.start()

        else:

            self.timer.stop()

        self._sync_play_icon()

    def _sync_play_icon(self):

        self.playButton.set_icon("pause" if self.running else "play")

    def _tick(self):

        self.remaining_seconds -= 1

        if self.remaining_seconds <= 0:

            self._complete_phase()

            return

        self._sync_ring()

    def _complete_phase(self):

        self.timer.stop()

        self.running = False

        if self.phase == "focus":

            self.focus_manager.log_session(self.focus_minutes)

            self.sessions_today += 1

            notify(
                f"Focus session complete — {self.focus_minutes} min logged.",
                "success"
            )

            self.phase = "break"

            self.total_seconds = self.break_minutes * 60

        else:

            notify(
                "Break's over — ready for another round?",
                "info"
            )

            self.phase = "focus"

            self.total_seconds = self.focus_minutes * 60

        self.remaining_seconds = self.total_seconds

        self._sync_ring()

        self._sync_play_icon()

        self.refresh_stats()

    def _sync_ring(self):

        elapsed = self.total_seconds - self.remaining_seconds

        percent = (
            round((elapsed / self.total_seconds) * 100)
            if self.total_seconds
            else 0
        )

        self.ring.setValue(percent)

        minutes, seconds = divmod(max(0, self.remaining_seconds), 60)

        self.ring.setLabel(f"{minutes:02d}:{seconds:02d}")

        self.phaseLabel.setText(
            "FOCUS SESSION" if self.phase == "focus" else "BREAK"
        )

    # -----------------------------------------------------------------
    # stats
    # -----------------------------------------------------------------

    @staticmethod
    def _format_minutes(total_minutes):

        if total_minutes >= 60:

            hours, minutes = divmod(total_minutes, 60)

            return f"{hours}h {minutes}m" if minutes else f"{hours}h"

        return f"{total_minutes}m"

    def refresh_stats(self):

        self.todayCard._valueLabel.setText(
            self._format_minutes(self.focus_manager.get_today_minutes())
        )

        self.weekCard._valueLabel.setText(
            self._format_minutes(self.focus_manager.get_week_minutes())
        )

        self.sessionsCard._valueLabel.setText(
            str(self.sessions_today)
        )

    # -----------------------------------------------------------------
    # theme
    # -----------------------------------------------------------------

    def apply_theme(self):

        theme = ThemeManager.get()

        style = ThemeManager.style()

        accent = theme.Colors.PRIMARY

        self.title.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:32px; font-weight:800; background:transparent;"
        )

        self.subtitle.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:15px; background:transparent;"
        )

        self.phaseLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:13px; font-weight:800; "
            "letter-spacing:2px; background:transparent; border:none;"
        )

        self.timerCard.setStyleSheet(
            f"""
            QFrame#timerCard{{
                background:{theme.Colors.GLASS};
                border:1px solid {theme.Colors.BORDER};
                border-radius:26px;
            }}
            """
        )

        self.ring.setColors(
            accent,
            qcolor(theme.Colors.TEXT, 0.14),
            theme.Colors.TEXT
        )

        glow = style.GLOW

        for button, diameter in (
            (self.playButton, 64),
            (self.resetButton, 48),
        ):

            button.setStyleSheet(
                f"""
                QPushButton{{
                    background:{rgba(accent, 0.85 if button is self.playButton else 0.16)};
                    border:1px solid {rgba(accent, 0.9 if button is self.playButton else 0.4)};
                    border-radius:{diameter // 2}px;
                }}
                QPushButton:hover{{
                    background:{rgba(accent, 0.95 if button is self.playButton else 0.28)};
                }}
                """
            )

            if glow > 0 and button is self.playButton:

                apply_glow(button, accent, blur=30, y_offset=6, alpha=int(200 * glow))

        preset_style = f"""
            QPushButton{{
                color:{theme.Colors.TEXT};
                background:{theme.Colors.GLASS};
                border:1px solid {theme.Colors.BORDER};
                border-radius:11px;
                padding:6px 14px;
                font-size:12px;
                font-weight:600;
            }}
            QPushButton:hover{{
                background:{theme.Colors.GLASS_HOVER};
                border:1px solid {rgba(accent, 0.5)};
            }}
        """

        for button, _f, _b in self.presetButtons:

            button.setStyleSheet(preset_style)

        self.customApply.setStyleSheet(preset_style)

        self.customSpin.setStyleSheet(
            f"""
            QSpinBox{{
                color:{theme.Colors.TEXT};
                background:{theme.Colors.GLASS};
                border:1px solid {theme.Colors.BORDER};
                border-radius:11px;
                padding:5px 8px;
            }}
            """
        )

        for card in (self.todayCard, self.weekCard, self.sessionsCard):

            card.setStyleSheet(
                f"""
                QFrame{{
                    background:{theme.Colors.GLASS};
                    border:1px solid {theme.Colors.BORDER};
                    border-radius:18px;
                }}
                """
            )

            card._titleLabel.setStyleSheet(
                f"color:{theme.Colors.TEXT_SECONDARY}; font-size:12px; "
                "background:transparent; border:none;"
            )

            card._valueLabel.setStyleSheet(
                f"color:{theme.Colors.TEXT}; font-size:22px; font-weight:800; "
                "background:transparent; border:none;"
            )

    def refresh_theme(self):

        self.apply_theme()

        self.refresh_stats()

    def showEvent(self, event):

        super().showEvent(event)

        self.refresh_stats()
