from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.design_system import HeaderPill, IconCircle, Metrics, SurfaceCard
from ui.icons import IconGlyph
from ui.progress_ring import ProgressRing
from ui.toast import notify
from utils.focus_manager import FocusManager
from utils.settings_manager import SettingsManager


class FocusWeekChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = [0] * 7
        self.setMinimumHeight(150)

    def set_values(self, values):
        values = list(values or [])[:7]
        self.values = values + [0] * (7 - len(values))
        self.update()

    def paintEvent(self, event):
        c = ThemeManager.get().Colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        chart = self.rect().adjusted(8, 10, -8, -28)
        labels = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        max_value = max(30, max(self.values))

        painter.setPen(QPen(QColor(c.BORDER), 1))

        for i in range(4):
            y = chart.top() + chart.height() * i / 3
            painter.drawLine(chart.left(), int(y), chart.right(), int(y))

        gap = 11
        bar_width = max(12, int((chart.width() - gap * 8) / 7))

        gradient = QLinearGradient(0, chart.bottom(), 0, chart.top())
        gradient.setColorAt(0.0, QColor(c.PRIMARY))
        gradient.setColorAt(1.0, QColor(c.PRIMARY_LIGHT))

        for i, minutes in enumerate(self.values):
            x = chart.left() + gap + i * (bar_width + gap)
            height = max(4, int(chart.height() * minutes / max_value)) if minutes else 3

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 5))
            painter.drawRoundedRect(
                QRectF(x - 3, chart.top(), bar_width + 6, chart.height()),
                4,
                4,
            )

            painter.setBrush(gradient)
            painter.drawRoundedRect(
                QRectF(x, chart.bottom() - height, bar_width, height),
                5,
                5,
            )

            painter.setPen(QColor(c.TEXT_SECONDARY))
            painter.drawText(
                QRectF(x - 8, chart.bottom() + 7, bar_width + 16, 18),
                Qt.AlignmentFlag.AlignCenter,
                labels[i],
            )


class RoundIconButton(QPushButton):
    def __init__(self, icon_name, diameter=52, primary=False, parent=None):
        super().__init__(parent)
        self.primary = primary
        self.setFixedSize(diameter, diameter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = IconGlyph(icon_name, size=int(diameter * 0.38), stroke_width=2.0)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self.icon)

        self.apply_theme()

    def set_icon(self, icon_name):
        self.icon.name = icon_name
        self.icon.update()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.icon.setColor("#FFFFFF" if self.primary else c.TEXT)

        if self.primary:
            background = (
                "qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                f"stop:0 {c.PRIMARY_LIGHT},stop:1 {c.PRIMARY})"
            )
            border = "rgba(135,165,255,0.62)"
        else:
            background = c.SURFACE_ALT
            border = c.BORDER

        self.setStyleSheet(
            f"""
            QPushButton {{
                background:{background};
                border:1px solid {border};
                border-radius:{self.width() // 2}px;
            }}
            QPushButton:hover {{
                border-color:{c.BORDER_ACTIVE};
            }}
            """
        )


class FocusPage(QWidget):
    def __init__(self):
        super().__init__()

        self.focus_manager = FocusManager()
        self.settings_manager = SettingsManager()

        self.focus_minutes = 25
        self.break_minutes = 5
        self.phase = "focus"
        self.total_seconds = self.focus_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.running = False

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)

        root = QVBoxLayout(self)
        root.setContentsMargins(Metrics.PAGE_X, Metrics.PAGE_Y, Metrics.PAGE_X, Metrics.PAGE_Y)
        root.setSpacing(16)

        self.title = QLabel("Focus")
        self.title.setObjectName("focusTitle")

        self.subtitle = QLabel("Protect your attention. One clean session at a time.")
        self.subtitle.setObjectName("focusSubtitle")

        root.addWidget(self.title)
        root.addWidget(self.subtitle)

        body = QHBoxLayout()
        body.setSpacing(14)

        self.timer_card = SurfaceCard("Focus Session", "Stay with one thing until the timer ends.")
        self.timer_card.setMinimumWidth(510)

        timer_center = QVBoxLayout()
        timer_center.setSpacing(14)
        timer_center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.phase_label = QLabel("FOCUS")
        self.phase_label.setObjectName("focusPhase")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ring = ProgressRing(diameter=210, thickness=12)

        controls = QHBoxLayout()
        controls.setSpacing(14)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.reset_button = RoundIconButton("reset", 46, False)
        self.reset_button.clicked.connect(self.reset_timer)

        self.play_button = RoundIconButton("play", 62, True)
        self.play_button.clicked.connect(self.toggle_running)

        controls.addWidget(self.reset_button)
        controls.addWidget(self.play_button)

        self.preset_row = QHBoxLayout()
        self.preset_row.setSpacing(7)
        self.preset_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preset_buttons = []

        for label, focus_minutes, break_minutes in (
            ("Pomodoro", 25, 5),
            ("Deep Work", 50, 10),
            ("Short Break", 5, 5),
            ("Long Break", 15, 5),
        ):
            button = QPushButton(label)
            button.setObjectName("focusPreset")
            button.setProperty("active", focus_minutes == 25)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, f=focus_minutes, b=break_minutes:
                    self.apply_preset(f, b)
            )
            self.preset_buttons.append((button, focus_minutes, break_minutes))
            self.preset_row.addWidget(button)

        custom_row = QHBoxLayout()
        custom_row.setSpacing(8)
        custom_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.custom_spin = QSpinBox()
        self.custom_spin.setObjectName("focusCustom")
        self.custom_spin.setRange(5, 180)
        self.custom_spin.setValue(25)
        self.custom_spin.setSuffix(" min")
        self.custom_spin.setFixedWidth(92)

        self.custom_button = QPushButton("Set Custom")
        self.custom_button.setObjectName("focusCustomButton")
        self.custom_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.custom_button.clicked.connect(
            lambda:
                self.apply_preset(
                    self.custom_spin.value(),
                    max(5, self.custom_spin.value() // 5),
                )
        )

        custom_row.addWidget(self.custom_spin)
        custom_row.addWidget(self.custom_button)

        timer_center.addWidget(self.phase_label)
        timer_center.addWidget(self.ring, 0, Qt.AlignmentFlag.AlignHCenter)
        timer_center.addLayout(controls)
        timer_center.addLayout(self.preset_row)
        timer_center.addLayout(custom_row)

        self.timer_card.body.addLayout(timer_center)
        body.addWidget(self.timer_card, 3)

        side = QVBoxLayout()
        side.setSpacing(12)

        stat_grid = QGridLayout()
        stat_grid.setSpacing(10)

        self.today_stat = self._stat_card("Today", "timer")
        self.week_stat = self._stat_card("This Week", "chart")
        self.sessions_stat = self._stat_card("Sessions Today", "check")
        self.goal_stat = self._stat_card("Weekly Goal", "star")

        for index, stat in enumerate((
            self.today_stat,
            self.week_stat,
            self.sessions_stat,
            self.goal_stat,
        )):
            stat_grid.addWidget(stat["frame"], index // 2, index % 2)

        side.addLayout(stat_grid)

        self.week_card = SurfaceCard("Weekly Rhythm")
        self.week_period = HeaderPill("This Week")
        self.week_card.set_header_action(self.week_period)

        self.week_chart = FocusWeekChart()
        self.week_card.body.addWidget(self.week_chart)
        side.addWidget(self.week_card, 1)

        self.tip_card = SurfaceCard("Session Tip")
        self.tip_text = QLabel(
            "Close the extra tabs. Put the phone away. Let the timer be the only deadline."
        )
        self.tip_text.setObjectName("focusTip")
        self.tip_text.setWordWrap(True)
        self.tip_card.body.addWidget(self.tip_text)

        side.addWidget(self.tip_card)

        side_wrap = QWidget()
        side_wrap.setLayout(side)
        body.addWidget(side_wrap, 2)

        root.addLayout(body, 1)

        self.apply_theme()
        self._sync_ring()
        self.refresh_stats()

    def _stat_card(self, label, icon_name):
        frame = QFrame()
        frame.setObjectName("focusStat")

        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(9)

        icon = IconCircle(icon_name, 38)

        text = QVBoxLayout()
        text.setSpacing(0)

        value = QLabel("0")
        value.setObjectName("focusStatValue")

        caption = QLabel(label)
        caption.setObjectName("focusStatCaption")

        text.addWidget(value)
        text.addWidget(caption)

        row.addWidget(icon)
        row.addLayout(text, 1)

        return {
            "frame": frame,
            "icon": icon,
            "value": value,
            "caption": caption,
        }

    def apply_preset(self, focus_minutes, break_minutes):
        self.timer.stop()
        self.running = False
        self.focus_minutes = int(focus_minutes)
        self.break_minutes = int(break_minutes)
        self.phase = "break" if focus_minutes in (5, 15) else "focus"
        self.total_seconds = self.focus_minutes * 60
        self.remaining_seconds = self.total_seconds

        for button, minutes, _break in self.preset_buttons:
            button.setProperty("active", minutes == self.focus_minutes)
            button.style().unpolish(button)
            button.style().polish(button)

        self._sync_play_icon()
        self._sync_ring()

    def reset_timer(self):
        self.timer.stop()
        self.running = False
        self.remaining_seconds = self.total_seconds
        self._sync_play_icon()
        self._sync_ring()

    def toggle_running(self):
        self.running = not self.running

        if self.running:
            self.timer.start()
        else:
            self.timer.stop()

        self._sync_play_icon()

    def _sync_play_icon(self):
        self.play_button.set_icon("pause" if self.running else "play")

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
            notify(
                f"Focus session complete — {self.focus_minutes} min logged.",
                "success",
            )
            self.phase = "break"
            self.total_seconds = self.break_minutes * 60
        else:
            notify("Break complete — ready for another round?", "info")
            self.phase = "focus"
            self.total_seconds = 25 * 60
            self.focus_minutes = 25

        self.remaining_seconds = self.total_seconds
        self._sync_play_icon()
        self._sync_ring()
        self.refresh_stats()

    def _sync_ring(self):
        elapsed = self.total_seconds - self.remaining_seconds
        percent = (
            round(elapsed / self.total_seconds * 100)
            if self.total_seconds
            else 0
        )

        self.ring.setValue(percent)

        minutes, seconds = divmod(max(0, self.remaining_seconds), 60)
        self.ring.setLabel(f"{minutes:02d}:{seconds:02d}")

        self.phase_label.setText(
            "FOCUS SESSION"
            if self.phase == "focus"
            else "BREAK"
        )

    @staticmethod
    def _format_minutes(total_minutes):
        total_minutes = max(0, int(total_minutes or 0))
        hours, minutes = divmod(total_minutes, 60)
        if hours:
            return f"{hours}h {minutes}m" if minutes else f"{hours}h"
        return f"{minutes}m"

    def refresh_stats(self):
        today = self.focus_manager.get_today_minutes()
        week = self.focus_manager.get_week_minutes()
        sessions = self.focus_manager.get_today_sessions()
        goal = int(
            self.settings_manager.get(
                "focus_weekly_goal_minutes",
                "1500",
            )
            or 1500
        )

        self.today_stat["value"].setText(
            self._format_minutes(today)
        )
        self.week_stat["value"].setText(
            self._format_minutes(week)
        )
        self.sessions_stat["value"].setText(str(sessions))
        self.goal_stat["value"].setText(
            f"{min(100, round(week / goal * 100)) if goal else 0}%"
        )

        self.week_chart.set_values(
            self.focus_manager.get_week_by_day()
        )

    def apply_theme(self):
        c = ThemeManager.get().Colors

        self.timer_card.apply_theme()
        self.week_card.apply_theme()
        self.tip_card.apply_theme()
        self.week_period.apply_theme()

        for stat in (
            self.today_stat,
            self.week_stat,
            self.sessions_stat,
            self.goal_stat,
        ):
            stat["icon"].apply_theme()

        self.reset_button.apply_theme()
        self.play_button.apply_theme()

        self.ring.setColors(
            c.PRIMARY_LIGHT,
            QColor(255, 255, 255, 24),
            c.TEXT,
        )

        self.setStyleSheet(
            f"""
            QLabel#focusTitle {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:28px;
                font-weight:800;
            }}

            QLabel#focusSubtitle {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:12px;
            }}

            QLabel#focusPhase {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:10px;
                font-weight:800;
                letter-spacing:2px;
            }}

            QPushButton#focusPreset {{
                color:{c.TEXT_SECONDARY};
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:9px;
                padding:7px 11px;
                font-size:10px;
            }}

            QPushButton#focusPreset:hover {{
                color:{c.TEXT};
                border-color:{c.BORDER_ACTIVE};
            }}

            QPushButton#focusPreset[active="true"] {{
                color:{c.TEXT};
                background:rgba(79,103,244,0.20);
                border-color:{c.PRIMARY_LIGHT};
            }}

            QSpinBox#focusCustom {{
                color:{c.TEXT};
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:9px;
                padding:7px 9px;
                font-size:10px;
            }}

            QPushButton#focusCustomButton {{
                color:{c.TEXT};
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:9px;
                padding:7px 12px;
                font-size:10px;
            }}

            QPushButton#focusCustomButton:hover {{
                border-color:{c.BORDER_ACTIVE};
            }}

            QFrame#focusStat {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:13px;
            }}

            QLabel#focusStatValue {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:17px;
                font-weight:800;
            }}

            QLabel#focusStatCaption {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:9px;
            }}

            QLabel#focusTip {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:10px;
            }}
            """
        )

    def refresh_theme(self):
        self.apply_theme()
        self.refresh_stats()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.refresh_stats)
