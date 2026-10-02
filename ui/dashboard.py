from datetime import date, datetime, timedelta

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.icons import IconGlyph
from utils.focus_manager import FocusManager
from utils.habit_manager import HabitManager
from utils.settings_manager import SettingsManager
from utils.task_manager import TaskManager


def _format_focus(minutes):

    minutes = max(0, int(minutes or 0))

    if minutes >= 60:
        hours, mins = divmod(minutes, 60)
        return f"{hours}h {mins}m" if mins else f"{hours}h"

    return f"{minutes}m"


class Card(QFrame):

    def __init__(self, title="", subtitle="", parent=None):

        super().__init__(parent)

        self.setObjectName("dashboardCard")

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(20, 18, 20, 18)
        self.root.setSpacing(10)

        if title:

            top = QHBoxLayout()

            self.title = QLabel(title)
            self.title.setObjectName("cardTitle")

            top.addWidget(self.title)

            if subtitle:
                sub = QLabel(subtitle)
                sub.setObjectName("cardSubtitle")
                top.addWidget(sub)

            top.addStretch(1)

            self.root.addLayout(top)


class WeeklyBars(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.values = [0] * 7
        self.setMinimumHeight(140)


    def set_values(self, values):

        self.values = list(values[:7]) + [0] * max(0, 7 - len(values))
        self.update()


    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = ThemeManager.get()
        c = theme.Colors

        left = 12
        right = 8
        top = 10
        bottom = 26

        area = self.rect().adjusted(left, top, -right, -bottom)

        grid_pen = QPen(QColor(c.BORDER))
        grid_pen.setWidthF(1.0)
        painter.setPen(grid_pen)

        for i in range(5):
            y = area.top() + area.height() * i / 4
            painter.drawLine(area.left(), int(y), area.right(), int(y))

        max_value = max(1, max(self.values))

        gap = 13
        bar_w = max(10, int((area.width() - gap * 8) / 7))

        accent = QColor(c.PRIMARY)
        accent2 = QColor(c.PURPLE)

        labels = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

        for index, value in enumerate(self.values):

            x = area.left() + gap + index * (bar_w + gap)
            ratio = value / max_value if max_value else 0
            height = max(6, int(area.height() * ratio * 0.88)) if value else 4
            y = area.bottom() - height

            color = QColor(accent)
            if index == max(range(7), key=lambda i: self.values[i]) and value:
                color = QColor(accent2)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(
                QRectF(x, y, bar_w, height),
                5,
                5
            )

            painter.setPen(QColor(c.TEXT_SECONDARY))
            label_rect = QRectF(
                x - 5,
                area.bottom() + 7,
                bar_w + 10,
                18
            )
            painter.drawText(
                label_rect,
                Qt.AlignmentFlag.AlignCenter,
                labels[index]
            )


class Donut(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.percent = 0
        self.label = "Overall"
        self.setFixedSize(150, 150)


    def set_value(self, percent):

        self.percent = max(0, min(100, int(percent)))
        self.update()


    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        theme = ThemeManager.get()
        c = theme.Colors

        rect = QRectF(16, 16, self.width() - 32, self.height() - 32)

        pen = QPen(QColor(c.SURFACE_ALT), 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        pen = QPen(QColor(c.PRIMARY), 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        start = 90 * 16
        span = -int(360 * 16 * self.percent / 100)
        painter.drawArc(rect, start, span)

        painter.setPen(QColor(c.TEXT))
        font = painter.font()
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(
            self.rect().adjusted(0, 24, 0, -12),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.percent}%"
        )

        painter.setPen(QColor(c.TEXT_SECONDARY))
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)

        painter.drawText(
            self.rect().adjusted(0, 82, 0, 0),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            self.label
        )


class MiniFocus(Card):

    def __init__(self, parent=None):

        super().__init__("Focus Timer", parent=parent)

        self.mode_minutes = 25
        self.remaining = 25 * 60
        self.running = False

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)

        line = QHBoxLayout()

        self.timeLabel = QLabel("25:00")
        self.timeLabel.setObjectName("focusTime")

        self.modeLabel = QLabel("Deep Work")
        self.modeLabel.setObjectName("mutedText")

        self.play = QPushButton("▶")
        self.play.setObjectName("focusPlay")
        self.play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play.setFixedSize(62, 62)
        self.play.clicked.connect(self.toggle)

        line.addWidget(self.timeLabel)
        line.addSpacing(16)
        line.addWidget(self.modeLabel)
        line.addStretch(1)
        line.addWidget(self.play)

        self.root.addLayout(line)

        presets = QHBoxLayout()
        presets.setSpacing(8)

        for text, minutes in (
            ("Pomodoro", 25),
            ("Short Break", 5),
            ("Long Break", 15),
        ):

            button = QPushButton(text)
            button.setObjectName("focusPreset")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, m=minutes: self.set_minutes(m)
            )

            presets.addWidget(button)

        self.root.addLayout(presets)


    def set_minutes(self, minutes):

        self.timer.stop()
        self.running = False
        self.play.setText("▶")

        self.mode_minutes = int(minutes)
        self.remaining = self.mode_minutes * 60

        self._sync()


    def toggle(self):

        self.running = not self.running

        if self.running:
            self.timer.start()
            self.play.setText("Ⅱ")
        else:
            self.timer.stop()
            self.play.setText("▶")


    def _tick(self):

        self.remaining -= 1

        if self.remaining <= 0:

            self.timer.stop()
            self.running = False
            self.play.setText("▶")

            if self.mode_minutes == 25:

                manager = FocusManager()
                manager.log_session(25)
                manager.close()

            self.remaining = self.mode_minutes * 60

        self._sync()


    def _sync(self):

        minutes, seconds = divmod(max(0, self.remaining), 60)
        self.timeLabel.setText(f"{minutes:02d}:{seconds:02d}")


class Dashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.task_manager = TaskManager()
        self.focus_manager = FocusManager()
        self.habit_manager = HabitManager()
        self.settings_manager = SettingsManager()

        self.user_name = self.settings_manager.get_user_name()

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 24)
        root.setSpacing(18)

        header = QHBoxLayout()

        heading_box = QVBoxLayout()
        heading_box.setSpacing(2)

        self.hello = QLabel("Good evening")
        self.hello.setObjectName("eyebrow")

        self.hero = QLabel("Let’s make it count.")
        self.hero.setObjectName("heroTitle")

        heading_box.addWidget(self.hello)
        heading_box.addWidget(self.hero)

        self.search = QLineEdit()
        self.search.setObjectName("topSearch")
        self.search.setPlaceholderText("Search anything…")
        self.search.setFixedWidth(310)
        self.search.textChanged.connect(self.refresh_recent)

        self.dateLabel = QLabel()
        self.dateLabel.setObjectName("topDate")

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(self.search, 0, Qt.AlignmentFlag.AlignRight)
        right.addWidget(self.dateLabel, 0, Qt.AlignmentFlag.AlignRight)

        header.addLayout(heading_box, 1)
        header.addLayout(right)

        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        grid.setColumnStretch(0, 11)
        grid.setColumnStretch(1, 10)

        self.weekCard = Card(
            "Weekly Overview",
            "Tasks, habits and focus at a glance."
        )
        self.weekBars = WeeklyBars()
        self.weekCard.root.addWidget(self.weekBars, 1)

        self.progressCard = Card("Progress")

        progress_content = QHBoxLayout()
        progress_content.setSpacing(16)

        self.donut = Donut()

        progress_content.addWidget(self.donut)

        progress_rows = QVBoxLayout()
        progress_rows.setSpacing(10)

        self.taskProgress = self._progress_row("Tasks", "0 / 0")
        self.habitProgress = self._progress_row("Habits", "0%")
        self.focusProgress = self._progress_row("Focus", "0h")

        for row in (
            self.taskProgress,
            self.habitProgress,
            self.focusProgress
        ):
            progress_rows.addLayout(row["layout"])

        progress_content.addLayout(progress_rows, 1)
        self.progressCard.root.addLayout(progress_content)

        self.focusCard = MiniFocus()

        self.habitsCard = Card("Habits")
        self.habitRows = QVBoxLayout()
        self.habitRows.setSpacing(7)
        self.habitsCard.root.addLayout(self.habitRows)

        self.recentCard = Card("Recent Tasks")
        self.recentRows = QVBoxLayout()
        self.recentRows.setSpacing(2)
        self.recentCard.root.addLayout(self.recentRows)

        self.statsCard = Card("Quick Stats")
        self.statsGrid = QGridLayout()
        self.statsGrid.setSpacing(10)

        self.statWidgets = []

        stats = (
            ("Tasks completed", "check"),
            ("Focus time", "timer"),
            ("Day streak", "flame"),
            ("Habit completion", "chart"),
        )

        for i, (label, icon) in enumerate(stats):

            widget = self._stat_tile(label, icon)
            self.statWidgets.append(widget)

            self.statsGrid.addWidget(
                widget["frame"],
                i // 2,
                i % 2
            )

        self.statsCard.root.addLayout(self.statsGrid)

        grid.addWidget(self.weekCard, 0, 0)
        grid.addWidget(self.progressCard, 0, 1)
        grid.addWidget(self.focusCard, 1, 0)
        grid.addWidget(self.habitsCard, 1, 1)
        grid.addWidget(self.recentCard, 2, 0)
        grid.addWidget(self.statsCard, 2, 1)

        root.addLayout(grid, 1)

        self.apply_theme()
        self.refresh_data()


    def _progress_row(self, label, value):

        layout = QVBoxLayout()
        layout.setSpacing(4)

        top = QHBoxLayout()

        title = QLabel(label)
        title.setObjectName("progressLabel")

        value_label = QLabel(value)
        value_label.setObjectName("progressValue")

        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(value_label)

        bar = QProgressBar()
        bar.setObjectName("dashboardProgress")
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setFixedHeight(7)

        layout.addLayout(top)
        layout.addWidget(bar)

        return {
            "layout": layout,
            "label": title,
            "value": value_label,
            "bar": bar,
        }


    def _stat_tile(self, label, icon_name):

        frame = QFrame()
        frame.setObjectName("statTile")

        row = QHBoxLayout(frame)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(10)

        icon_box = QFrame()
        icon_box.setObjectName("statIconBox")
        icon_box.setFixedSize(42, 42)

        icon_layout = QHBoxLayout(icon_box)
        icon_layout.setContentsMargins(10, 10, 10, 10)

        icon = IconGlyph(icon_name, size=22)
        icon_layout.addWidget(icon)

        text_box = QVBoxLayout()
        text_box.setSpacing(0)

        value = QLabel("0")
        value.setObjectName("statValue")

        caption = QLabel(label)
        caption.setObjectName("statCaption")

        text_box.addWidget(value)
        text_box.addWidget(caption)

        row.addWidget(icon_box)
        row.addLayout(text_box, 1)

        return {
            "frame": frame,
            "icon": icon,
            "value": value,
            "caption": caption,
        }


    def set_user_name(self, name):

        self.user_name = (name or "").strip()
        self._sync_greeting()


    def _sync_greeting(self):

        hour = datetime.now().hour

        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        if self.user_name:
            greeting += f", {self.user_name.split()[0]}"

        self.hello.setText(greeting)


    def refresh_data(self):

        self._sync_greeting()

        self.dateLabel.setText(
            datetime.now().strftime("%a, %b %d, %Y")
        )

        tasks = self.task_manager.get_all_tasks()
        completed = [task for task in tasks if task.completed]

        weekly_goal = int(
            self.settings_manager.get("weekly_goal", "35") or 35
        )

        week = self.task_manager.get_week_completion(weekly_goal)

        self.weekBars.set_values(week["counts"])

        task_percent = (
            round((len(completed) / len(tasks)) * 100)
            if tasks
            else 0
        )

        habit_percent = self.habit_manager.week_completion_percent()

        focus_minutes = self.focus_manager.get_week_minutes()
        focus_goal = 25 * 60
        focus_percent = min(
            100,
            round((focus_minutes / focus_goal) * 100)
        )

        overall = round(
            (task_percent + habit_percent + focus_percent) / 3
        )

        self.donut.set_value(overall)

        self.taskProgress["value"].setText(
            f"{len(completed)} / {len(tasks)}"
        )
        self.taskProgress["bar"].setValue(task_percent)

        self.habitProgress["value"].setText(
            f"{habit_percent}%"
        )
        self.habitProgress["bar"].setValue(habit_percent)

        self.focusProgress["value"].setText(
            _format_focus(focus_minutes)
        )
        self.focusProgress["bar"].setValue(focus_percent)

        self.statWidgets[0]["value"].setText(
            str(len(completed))
        )
        self.statWidgets[1]["value"].setText(
            _format_focus(focus_minutes)
        )
        self.statWidgets[2]["value"].setText(
            str(self.task_manager.calculate_streak())
        )
        self.statWidgets[3]["value"].setText(
            f"{habit_percent}%"
        )

        self.refresh_habits()
        self.refresh_recent()


    def refresh_recent(self):

        if not hasattr(self, "recentRows"):
            return

        while self.recentRows.count():

            item = self.recentRows.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        text = self.search.text().strip().lower()

        tasks = self.task_manager.get_all_tasks()

        if text:
            tasks = [
                task
                for task in tasks
                if (
                    text in task.title.lower()
                    or text in task.category.lower()
                )
            ]

        tasks = tasks[:5]

        if not tasks:

            empty = QLabel("No tasks yet.")
            empty.setObjectName("mutedText")
            self.recentRows.addWidget(empty)
            return

        for task in tasks:

            row = QFrame()
            row.setObjectName("recentTaskRow")

            layout = QHBoxLayout(row)
            layout.setContentsMargins(2, 7, 2, 7)
            layout.setSpacing(10)

            done = QPushButton("✓" if task.completed else "")
            done.setObjectName("taskDotDone" if task.completed else "taskDot")
            done.setFixedSize(23, 23)
            done.setCursor(Qt.CursorShape.PointingHandCursor)
            done.clicked.connect(
                lambda _checked=False, t=task:
                    self._toggle_task(t)
            )

            title = QLabel(task.title)
            title.setObjectName(
                "recentDoneTitle"
                if task.completed
                else "recentTaskTitle"
            )

            when = QLabel(
                task.task_date or "Today"
            )
            when.setObjectName("mutedText")

            layout.addWidget(done)
            layout.addWidget(title, 1)
            layout.addWidget(when)

            self.recentRows.addWidget(row)


    def _toggle_task(self, task):

        self.task_manager.complete_task(
            task.id,
            not task.completed
        )

        self.refresh_data()


    def refresh_habits(self):

        while self.habitRows.count():

            item = self.habitRows.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        habits = self.habit_manager.get_habits_with_week()

        day_header = QHBoxLayout()
        day_header.addSpacing(155)

        for day in ("M", "T", "W", "T", "F", "S", "S"):

            label = QLabel(day)
            label.setObjectName("habitDayHead")
            label.setFixedWidth(28)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_header.addWidget(label)

        header_wrap = QWidget()
        header_wrap.setLayout(day_header)
        self.habitRows.addWidget(header_wrap)

        for habit in habits[:5]:

            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)

            name = QLabel(habit["name"])
            name.setObjectName("habitName")
            name.setFixedWidth(145)

            row.addWidget(name)

            for day_iso, checked in habit["week"]:

                cell = QPushButton("✓" if checked else "")
                cell.setObjectName(
                    "habitCellOn"
                    if checked
                    else "habitCell"
                )
                cell.setFixedSize(28, 28)
                cell.setCursor(Qt.CursorShape.PointingHandCursor)
                cell.clicked.connect(
                    lambda _checked=False, hid=habit["id"], d=day_iso:
                        self._toggle_habit(hid, d)
                )

                row.addWidget(cell)

            self.habitRows.addWidget(row_widget)


    def _toggle_habit(self, habit_id, day_iso):

        self.habit_manager.toggle_day(
            habit_id,
            day_iso
        )

        self.refresh_data()


    def apply_theme(self):

        theme = ThemeManager.get()
        c = theme.Colors

        self.setStyleSheet(
            f"""
            QWidget {{
                background:transparent;
            }}

            QFrame#dashboardCard {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:16px;
            }}

            QLabel#eyebrow {{
                color:{c.TEXT};
                font-size:23px;
                font-weight:700;
                background:transparent;
            }}

            QLabel#heroTitle {{
                color:{c.PRIMARY};
                font-size:34px;
                font-weight:900;
                background:transparent;
            }}

            QLabel#topDate,
            QLabel#cardSubtitle,
            QLabel#mutedText,
            QLabel#progressValue,
            QLabel#statCaption,
            QLabel#habitDayHead {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                font-size:11px;
            }}

            QLabel#cardTitle {{
                color:{c.TEXT};
                background:transparent;
                font-size:17px;
                font-weight:800;
            }}

            QLabel#progressLabel,
            QLabel#habitName {{
                color:{c.TEXT};
                background:transparent;
                font-size:12px;
                font-weight:600;
            }}

            QLineEdit#topSearch {{
                background:{c.SURFACE};
                color:{c.TEXT};
                border:1px solid {c.BORDER};
                border-radius:16px;
                padding:9px 14px;
                font-size:12px;
            }}

            QLineEdit#topSearch:focus {{
                border-color:{c.BORDER_ACTIVE};
            }}

            QProgressBar#dashboardProgress {{
                background:{c.SURFACE_ALT};
                border:none;
                border-radius:3px;
            }}

            QProgressBar#dashboardProgress::chunk {{
                background:{c.PRIMARY};
                border-radius:3px;
            }}

            QLabel#focusTime {{
                color:{c.TEXT};
                background:transparent;
                font-size:42px;
                font-weight:800;
            }}

            QPushButton#focusPlay {{
                background:{c.PRIMARY};
                color:white;
                border:1px solid {c.BORDER_ACTIVE};
                border-radius:31px;
                font-size:23px;
                font-weight:800;
            }}

            QPushButton#focusPreset {{
                background:{c.SURFACE_ALT};
                color:{c.TEXT_SECONDARY};
                border:1px solid {c.BORDER};
                border-radius:15px;
                padding:8px 13px;
                font-size:11px;
            }}

            QPushButton#focusPreset:hover {{
                color:{c.TEXT};
                border-color:{c.BORDER_ACTIVE};
            }}

            QFrame#recentTaskRow {{
                border:none;
                border-bottom:1px solid {c.BORDER};
                background:transparent;
            }}

            QLabel#recentTaskTitle {{
                color:{c.TEXT};
                background:transparent;
                font-size:12px;
            }}

            QLabel#recentDoneTitle {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                font-size:12px;
                text-decoration:line-through;
            }}

            QPushButton#taskDot,
            QPushButton#taskDotDone {{
                border-radius:11px;
                border:1px solid {c.TEXT_SECONDARY};
                color:white;
                background:transparent;
                font-weight:800;
            }}

            QPushButton#taskDotDone {{
                background:{c.PRIMARY};
                border-color:{c.PRIMARY};
            }}

            QFrame#statTile {{
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:13px;
            }}

            QFrame#statIconBox {{
                background:rgba(80,130,255,0.15);
                border:1px solid rgba(80,130,255,0.20);
                border-radius:21px;
            }}

            QLabel#statValue {{
                color:{c.TEXT};
                background:transparent;
                font-size:20px;
                font-weight:800;
            }}

            QPushButton#habitCell,
            QPushButton#habitCellOn {{
                background:{c.SURFACE_ALT};
                color:white;
                border:1px solid {c.BORDER};
                border-radius:5px;
                font-size:11px;
                font-weight:800;
            }}

            QPushButton#habitCellOn {{
                background:{c.PRIMARY};
                border-color:{c.BORDER_ACTIVE};
            }}
            """
        )

        for stat in self.statWidgets:
            stat["icon"].setColor(c.PRIMARY)

        self.weekBars.update()
        self.donut.update()


    def refresh_theme(self):

        self.apply_theme()
        self.refresh_data()


    def showEvent(self, event):

        super().showEvent(event)
        QTimer.singleShot(0, self.refresh_data)
