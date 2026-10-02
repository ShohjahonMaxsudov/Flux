from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRectF, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.design_system import AccentOrb, CheckButton, HeaderLink, HeaderPill, IconCircle, Metrics, SurfaceCard, clear_layout
from ui.icons import IconGlyph
from utils.focus_manager import FocusManager
from utils.habit_manager import HabitManager
from utils.settings_manager import SettingsManager
from utils.task_manager import TaskManager


def _focus_text(minutes):
    minutes = max(0, int(minutes or 0))
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    return f"{mins}m"


class WeeklyBars(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = [0] * 7
        self.setMinimumHeight(145)

    def set_values(self, values):
        values = list(values or [])[:7]
        self.values = values + [0] * (7 - len(values))
        self.update()

    def paintEvent(self, event):
        c = ThemeManager.get().Colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        chart = self.rect().adjusted(38, 8, -8, -28)
        painter.setPen(QPen(QColor(c.BORDER), 1))

        for i in range(5):
            y = chart.top() + chart.height() * i / 4
            painter.drawLine(chart.left(), int(y), chart.right(), int(y))

        max_value = max(1, max(self.values))
        labels = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        gap = 12
        bar_w = max(12, int((chart.width() - gap * 8) / 7))

        for i in range(7):
            x = chart.left() + gap + i * (bar_w + gap)
            slot = QRectF(x - 5, chart.top(), bar_w + 10, chart.height())
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 5))
            painter.drawRoundedRect(slot, 3, 3)

        gradient = QLinearGradient(0, chart.bottom(), 0, chart.top())
        gradient.setColorAt(0.0, QColor(c.PRIMARY))
        gradient.setColorAt(1.0, QColor(c.PRIMARY_LIGHT))

        for i, value in enumerate(self.values):
            x = chart.left() + gap + i * (bar_w + gap)
            ratio = value / max_value if max_value else 0
            h = max(4, int(chart.height() * ratio * 0.88)) if value else 3
            y = chart.bottom() - h

            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_w, h), 5, 5)

            painter.setPen(QColor(c.TEXT_SECONDARY))
            painter.drawText(
                QRectF(x - 8, chart.bottom() + 7, bar_w + 16, 18),
                Qt.AlignmentFlag.AlignCenter,
                labels[i],
            )

        painter.setPen(QColor(c.TEXT_TERTIARY))
        for i, label in enumerate(("100%", "75%", "50%", "25%", "0%")):
            y = chart.top() + chart.height() * i / 4
            painter.drawText(
                QRectF(0, y - 8, 32, 16),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                label,
            )


class Donut(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percent = 0
        self.setFixedSize(150, 150)

    def set_value(self, value):
        self.percent = max(0, min(100, int(value)))
        self.update()

    def paintEvent(self, event):
        c = ThemeManager.get().Colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(15, 15, self.width() - 30, self.height() - 30)

        base = QPen(QColor("#202A39"), 12)
        base.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(base)
        painter.drawArc(rect, 0, 360 * 16)

        accent = QPen(QColor(c.PRIMARY_LIGHT), 12)
        accent.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(accent)
        painter.drawArc(
            rect,
            90 * 16,
            -int(360 * 16 * self.percent / 100),
        )

        painter.setPen(QColor(c.TEXT))
        font = painter.font()
        font.setPointSize(21)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            self.rect().adjusted(0, 24, 0, -18),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.percent}%",
        )

        painter.setPen(QColor(c.TEXT_SECONDARY))
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(
            self.rect().adjusted(0, 83, 0, 0),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            "Overall",
        )


class FocusTimerCard(SurfaceCard):
    completed = Signal()

    def __init__(self, parent=None):
        super().__init__("Focus Timer", parent=parent)
        self.minutes = 25
        self.remaining = self.minutes * 60
        self.running = False

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)

        top = QHBoxLayout()
        top.setSpacing(14)

        self.time_label = QLabel("25:00")
        self.time_label.setObjectName("focusClock")

        self.mode_label = QLabel("Deep Work")
        self.mode_label.setObjectName("focusMode")

        self.play = QPushButton()
        self.play.setObjectName("roundPlay")
        self.play.setFixedSize(60, 60)
        self.play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play.clicked.connect(self.toggle)

        play_layout = QHBoxLayout(self.play)
        play_layout.setContentsMargins(0, 0, 0, 0)
        play_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.play_icon = IconGlyph("play", size=24)
        self.play_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        play_layout.addWidget(self.play_icon)

        top.addWidget(self.time_label)
        top.addSpacing(12)
        top.addWidget(self.mode_label)
        top.addStretch(1)
        top.addWidget(self.play)
        self.body.addLayout(top)

        presets = QHBoxLayout()
        presets.setSpacing(8)
        self.preset_buttons = []
        for label, minutes in (("Pomodoro", 25), ("Short Break", 5), ("Long Break", 15)):
            button = QPushButton(label)
            button.setObjectName("focusPreset")
            button.setProperty("active", minutes == 25)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, m=minutes: self.set_minutes(m))
            presets.addWidget(button)
            self.preset_buttons.append((button, minutes))
        self.body.addLayout(presets)
        self.apply_theme()

    def set_minutes(self, minutes):
        self.timer.stop()
        self.running = False
        self.minutes = int(minutes)
        self.remaining = self.minutes * 60
        for button, value in self.preset_buttons:
            button.setProperty("active", value == self.minutes)
            button.style().unpolish(button)
            button.style().polish(button)
        self._sync()

    def toggle(self):
        self.running = not self.running
        if self.running:
            self.timer.start()
            self.play_icon.name = "pause"
        else:
            self.timer.stop()
            self.play_icon.name = "play"
        self.play_icon.update()

    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
            self.running = False
            self.play_icon.name = "play"
            self.play_icon.update()
            if self.minutes == 25:
                manager = FocusManager()
                manager.log_session(25)
                manager.close()
                self.completed.emit()
            self.remaining = self.minutes * 60
        self._sync()

    def _sync(self):
        minutes, seconds = divmod(max(0, self.remaining), 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def apply_theme(self):
        super().apply_theme()
        c = ThemeManager.get().Colors
        self.time_label.setStyleSheet(
            f"color:{c.TEXT}; background:transparent; border:none; font-size:36px; font-weight:800;"
        )
        self.mode_label.setStyleSheet(
            f"color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:12px;"
        )
        self.play_icon.setColor("#FFFFFF")
        self.play.setStyleSheet(
            f"""
            QPushButton#roundPlay {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {c.PRIMARY_LIGHT},stop:1 {c.PRIMARY});
                border:2px solid rgba(125,155,255,0.55);
                border-radius:30px;
            }}
            QPushButton#roundPlay:hover {{ border-color:rgba(210,220,255,0.90); }}
            """
        )
        for button, _minutes in self.preset_buttons:
            button.setStyleSheet(
                f"""
                QPushButton#focusPreset {{
                    color:{c.TEXT_SECONDARY};
                    background:{c.SURFACE_ALT};
                    border:1px solid {c.BORDER};
                    border-radius:10px;
                    padding:8px 14px;
                    font-size:11px;
                }}
                QPushButton#focusPreset[active="true"] {{
                    color:{c.TEXT};
                    background:rgba(79,103,244,0.22);
                    border-color:{c.PRIMARY_LIGHT};
                }}
                """
            )


class Dashboard(QWidget):
    navigateRequested = Signal(str)

    def __init__(self):
        super().__init__()

        self.task_manager = TaskManager()
        self.focus_manager = FocusManager()
        self.habit_manager = HabitManager()
        self.settings_manager = SettingsManager()
        self.user_name = self.settings_manager.get_user_name()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} QScrollArea>QWidget>QWidget{background:transparent;}")

        self.content = QWidget()
        self.content.setStyleSheet("background:transparent;")
        root = QVBoxLayout(self.content)
        root.setContentsMargins(Metrics.PAGE_X, Metrics.PAGE_Y, Metrics.PAGE_X, Metrics.PAGE_Y)
        root.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(18)

        left = QVBoxLayout()
        left.setSpacing(2)
        self.greeting = QLabel("Good evening")
        self.greeting.setObjectName("dashboardGreeting")
        self.hero = QLabel("Let’s make it count.")
        self.hero.setObjectName("dashboardHero")
        left.addWidget(self.greeting)
        left.addWidget(self.hero)

        right = QVBoxLayout()
        right.setSpacing(10)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        self.search = QLineEdit()
        self.search.setObjectName("dashboardSearch")
        self.search.setPlaceholderText("Search anything…")
        self.search.setFixedWidth(305)
        self.search.textChanged.connect(self.refresh_recent)
        self.avatar = AccentOrb(38)
        search_row.addWidget(self.search)
        search_row.addWidget(self.avatar)

        self.date_label = QLabel()
        self.date_label.setObjectName("dashboardDate")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        right.addLayout(search_row)
        right.addWidget(self.date_label)

        header.addLayout(left, 1)
        header.addLayout(right)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 11)
        grid.setColumnStretch(1, 10)

        self.week_card = SurfaceCard("Weekly Overview", "Tasks, habits and focus at a glance.")
        self.week_card.setMinimumHeight(244)
        self.week_details = HeaderLink("Details")
        self.week_details.clicked.connect(lambda: self.navigateRequested.emit("Statistics"))
        self.week_card.set_header_action(self.week_details)
        self.week_bars = WeeklyBars()
        self.week_card.body.addWidget(self.week_bars, 1)

        self.progress_card = SurfaceCard("Progress")
        self.progress_card.setMinimumHeight(244)
        self.progress_period = HeaderPill("This Week")
        self.progress_card.set_header_action(self.progress_period)
        progress_row = QHBoxLayout()
        progress_row.setSpacing(18)
        self.donut = Donut()
        progress_row.addWidget(self.donut)

        progress_metrics = QVBoxLayout()
        progress_metrics.setSpacing(13)
        self.task_progress = self._progress_metric("Tasks", "#4E9BFF")
        self.habit_progress = self._progress_metric("Habits", "#A66CFF")
        self.focus_progress = self._progress_metric("Focus", "#8FA8FF")
        for metric in (self.task_progress, self.habit_progress, self.focus_progress):
            progress_metrics.addLayout(metric["layout"])
        progress_row.addLayout(progress_metrics, 1)
        self.progress_card.body.addLayout(progress_row)

        self.focus_card = FocusTimerCard()
        self.focus_card.setMinimumHeight(192)
        self.focus_open = HeaderLink("Open")
        self.focus_open.clicked.connect(lambda: self.navigateRequested.emit("Focus"))
        self.focus_card.set_header_action(self.focus_open)
        self.focus_card.completed.connect(self.refresh_data)

        self.habits_card = SurfaceCard("Habits")
        self.habits_card.setMinimumHeight(192)
        self.habits_period = HeaderPill("This Week")
        self.habits_card.set_header_action(self.habits_period)
        self.habit_rows = QVBoxLayout()
        self.habit_rows.setSpacing(6)
        self.habits_card.body.addLayout(self.habit_rows)

        self.recent_card = SurfaceCard("Recent Tasks")
        self.recent_card.setMinimumHeight(205)
        self.recent_link = HeaderLink("View all")
        self.recent_link.clicked.connect(lambda: self.navigateRequested.emit("Tasks"))
        self.recent_card.set_header_action(self.recent_link)
        self.recent_rows = QVBoxLayout()
        self.recent_rows.setSpacing(0)
        self.recent_card.body.addLayout(self.recent_rows)

        self.stats_card = SurfaceCard("Quick Stats")
        self.stats_card.setMinimumHeight(205)
        self.stats_period = HeaderPill("This Week")
        self.stats_card.set_header_action(self.stats_period)
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(9)
        self.stat_widgets = []
        for i, (label, icon_name) in enumerate((
            ("Tasks completed", "check"),
            ("Focus time", "timer"),
            ("Day streak", "flame"),
            ("Habit completion", "chart"),
        )):
            tile = self._stat_tile(label, icon_name)
            self.stat_widgets.append(tile)
            self.stats_grid.addWidget(tile["frame"], i // 2, i % 2)
        self.stats_card.body.addLayout(self.stats_grid)

        grid.addWidget(self.week_card, 0, 0)
        grid.addWidget(self.progress_card, 0, 1)
        grid.addWidget(self.focus_card, 1, 0)
        grid.addWidget(self.habits_card, 1, 1)
        grid.addWidget(self.recent_card, 2, 0)
        grid.addWidget(self.stats_card, 2, 1)

        root.addLayout(grid)
        root.addStretch(1)

        self.scroll.setWidget(self.content)
        outer.addWidget(self.scroll)

        self.apply_theme()
        self.refresh_data()

    def _progress_metric(self, label, accent):
        layout = QVBoxLayout()
        layout.setSpacing(4)
        top = QHBoxLayout()
        top.setSpacing(7)

        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"background:{accent}; border:none; border-radius:4px;"
        )

        title = QLabel(label)
        title.setObjectName("progressLabel")
        value = QLabel("0")
        value.setObjectName("progressValue")

        top.addWidget(dot)
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(value)

        bar = QProgressBar()
        bar.setObjectName("dashboardProgress")
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(
            f"""
            QProgressBar#dashboardProgress {{
                background:#202A39;
                border:none;
                border-radius:3px;
            }}
            QProgressBar#dashboardProgress::chunk {{
                background:{accent};
                border-radius:3px;
            }}
            """
        )

        layout.addLayout(top)
        layout.addWidget(bar)
        return {"layout": layout, "value": value, "bar": bar, "dot": dot}

    def _stat_tile(self, label, icon_name):
        frame = QFrame()
        frame.setObjectName("statTile")
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)

        icon = IconCircle(icon_name, 40)
        text = QVBoxLayout()
        text.setSpacing(0)
        value = QLabel("0")
        value.setObjectName("statValue")
        caption = QLabel(label)
        caption.setObjectName("statCaption")
        text.addWidget(value)
        text.addWidget(caption)

        trend = QLabel("This week")
        trend.setObjectName("statTrend")
        trend.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(icon)
        row.addLayout(text, 1)
        row.addWidget(trend)
        return {"frame": frame, "icon": icon, "value": value, "caption": caption, "trend": trend}

    def set_user_name(self, name):
        self.user_name = (name or "").strip()
        self._sync_greeting()

    def _sync_greeting(self):
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
        if self.user_name:
            greeting += f", {self.user_name.split()[0]}"
        self.greeting.setText(greeting)

    def refresh_data(self):
        self._sync_greeting()
        self.date_label.setText(datetime.now().strftime("%a, %b %d, %Y"))

        tasks = self.task_manager.get_all_tasks()
        completed = [task for task in tasks if task.completed]

        weekly_goal = int(self.settings_manager.get("weekly_goal", "18") or 18)
        week = self.task_manager.get_week_completion(weekly_goal)
        self.week_bars.set_values(week["counts"])

        task_percent = round(len(completed) / len(tasks) * 100) if tasks else 0
        habit_percent = self.habit_manager.week_completion_percent()
        focus_minutes = self.focus_manager.get_week_minutes()
        focus_goal = int(self.settings_manager.get("focus_weekly_goal_minutes", "1500") or 1500)
        focus_percent = min(100, round(focus_minutes / focus_goal * 100)) if focus_goal else 0
        overall = round((task_percent + habit_percent + focus_percent) / 3)
        self.donut.set_value(overall)

        self.task_progress["value"].setText(f"{len(completed)} / {len(tasks)}")
        self.task_progress["bar"].setValue(task_percent)
        self.habit_progress["value"].setText(f"{habit_percent}%")
        self.habit_progress["bar"].setValue(habit_percent)
        self.focus_progress["value"].setText(f"{_focus_text(focus_minutes)} / {_focus_text(focus_goal)}")
        self.focus_progress["bar"].setValue(focus_percent)

        self.stat_widgets[0]["value"].setText(str(len(completed)))
        self.stat_widgets[1]["value"].setText(_focus_text(focus_minutes))
        self.stat_widgets[2]["value"].setText(str(self.task_manager.calculate_streak()))
        self.stat_widgets[3]["value"].setText(f"{habit_percent}%")

        self.refresh_habits()
        self.refresh_recent()

    def refresh_recent(self):
        clear_layout(self.recent_rows)
        query = self.search.text().strip().lower()
        tasks = self.task_manager.get_all_tasks()
        if query:
            tasks = [
                task for task in tasks
                if query in task.title.lower() or query in task.category.lower()
            ]
        tasks = tasks[:5]

        if not tasks:
            empty = QLabel("No matching tasks.")
            empty.setObjectName("dashboardMuted")
            self.recent_rows.addWidget(empty)
            return

        for task in tasks:
            row = QFrame()
            row.setObjectName("recentTask")
            layout = QHBoxLayout(row)
            layout.setContentsMargins(2, 7, 2, 7)
            layout.setSpacing(10)

            check = CheckButton(task.completed, size=22)
            check.clicked.connect(lambda _checked=False, t=task: self._toggle_task(t))

            title = QLabel(task.title)
            title.setObjectName("recentTitleDone" if task.completed else "recentTitle")

            when = QLabel(self._friendly_date(task.task_date))
            when.setObjectName("dashboardMuted")

            layout.addWidget(check)
            layout.addWidget(title, 1)
            layout.addWidget(when)
            self.recent_rows.addWidget(row)

    def _toggle_task(self, task):
        self.task_manager.complete_task(task.id, not task.completed)
        self.refresh_data()

    @staticmethod
    def _friendly_date(value):
        if not value:
            return "Today"
        try:
            day = datetime.strptime(value, "%Y-%m-%d").date()
            today = datetime.now().date()
            delta = (day - today).days
            if delta == 0:
                return "Today"
            if delta == 1:
                return "Tomorrow"
            return day.strftime("%b %d")
        except (TypeError, ValueError):
            return value

    def refresh_habits(self):
        clear_layout(self.habit_rows)
        c = ThemeManager.get().Colors
        habits = self.habit_manager.get_habits_with_week()[:5]

        header_widget = QWidget()
        header = QHBoxLayout(header_widget)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(5)
        header.addSpacing(155)
        for day in ("M", "T", "W", "T", "F", "S", "S"):
            label = QLabel(day)
            label.setObjectName("habitDay")
            label.setFixedWidth(27)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.addWidget(label)
        self.habit_rows.addWidget(header_widget)

        for habit in habits:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(5)

            dot = QFrame()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(
                f"background:{habit.get('color') or c.PRIMARY_LIGHT}; border:none; border-radius:5px;"
            )
            name = QLabel(habit["name"])
            name.setObjectName("habitName")
            name.setFixedWidth(131)

            row.addWidget(dot)
            row.addSpacing(6)
            row.addWidget(name)

            for day_iso, checked in habit["week"]:
                cell = CheckButton(checked, size=27, square=True)
                cell.clicked.connect(
                    lambda _checked=False, hid=habit["id"], day=day_iso: self._toggle_habit(hid, day)
                )
                row.addWidget(cell)

            self.habit_rows.addWidget(row_widget)

    def _toggle_habit(self, habit_id, day_iso):
        self.habit_manager.toggle_day(habit_id, day_iso)
        self.refresh_data()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        for card in (
            self.week_card, self.progress_card, self.focus_card,
            self.habits_card, self.recent_card, self.stats_card,
        ):
            card.apply_theme()

        self.setStyleSheet(
            f"""
            QLabel#dashboardGreeting {{
                color:{c.TEXT}; background:transparent; border:none;
                font-size:24px; font-weight:700;
            }}
            QLabel#dashboardHero {{
                color:{c.PRIMARY_LIGHT}; background:transparent; border:none;
                font-size:30px; font-weight:800;
            }}
            QLineEdit#dashboardSearch {{
                color:{c.TEXT}; background:{c.SURFACE};
                border:1px solid {c.BORDER}; border-radius:16px;
                padding:9px 14px; font-size:11px;
            }}
            QLineEdit#dashboardSearch:focus {{ border-color:{c.BORDER_ACTIVE}; }}
            QLabel#dashboardDate, QLabel#dashboardMuted, QLabel#habitDay {{
                color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px;
            }}
            QLabel#progressLabel {{ color:{c.TEXT}; background:transparent; border:none; font-size:11px; }}
            QLabel#progressValue {{ color:{c.TEXT}; background:transparent; border:none; font-size:11px; font-weight:700; }}
            QFrame#statTile {{ background:{c.SURFACE_ALT}; border:1px solid {c.BORDER}; border-radius:12px; }}
            QLabel#statValue {{ color:{c.TEXT}; background:transparent; border:none; font-size:19px; font-weight:800; }}
            QLabel#statCaption {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:9px; }}
            QLabel#statTrend {{ color:{c.GREEN}; background:transparent; border:none; font-size:9px; }}
            QFrame#recentTask {{ background:transparent; border:none; border-bottom:1px solid rgba(130,155,190,0.10); }}
            QLabel#recentTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:11px; }}
            QLabel#recentTitleDone {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:11px; text-decoration:line-through; }}
            QLabel#habitName {{ color:{c.TEXT}; background:transparent; border:none; font-size:10px; }}
            """
        )

    def refresh_theme(self):
        self.apply_theme()
        self.refresh_data()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.refresh_data)
