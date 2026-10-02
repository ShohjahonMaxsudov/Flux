from collections import Counter

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.design_system import HeaderPill, IconCircle, Metrics, SurfaceCard
from utils.focus_manager import FocusManager
from utils.habit_manager import HabitManager
from utils.task_manager import TaskManager


class PerformanceChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_values = [0] * 7
        self.focus_values = [0] * 7
        self.setMinimumHeight(190)

    def set_values(self, tasks, focus):
        tasks = list(tasks or [])[:7]
        focus = list(focus or [])[:7]
        self.task_values = tasks + [0] * (7 - len(tasks))
        self.focus_values = focus + [0] * (7 - len(focus))
        self.update()

    def paintEvent(self, event):
        c = ThemeManager.get().Colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        chart = self.rect().adjusted(36, 10, -12, -28)
        labels = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

        painter.setPen(QPen(QColor(c.BORDER), 1))
        for i in range(5):
            y = chart.top() + chart.height() * i / 4
            painter.drawLine(chart.left(), int(y), chart.right(), int(y))

        max_tasks = max(1, max(self.task_values))
        max_focus = max(25, max(self.focus_values))

        gap = 14
        bar_width = max(12, int((chart.width() - gap * 8) / 7))

        gradient = QLinearGradient(0, chart.bottom(), 0, chart.top())
        gradient.setColorAt(0.0, QColor(c.PRIMARY))
        gradient.setColorAt(1.0, QColor(c.PRIMARY_LIGHT))

        focus_points = []

        for i in range(7):
            x = chart.left() + gap + i * (bar_width + gap)

            task_height = (
                max(4, int(chart.height() * self.task_values[i] / max_tasks * 0.84))
                if self.task_values[i]
                else 3
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(
                QRectF(
                    x,
                    chart.bottom() - task_height,
                    bar_width,
                    task_height,
                ),
                5,
                5,
            )

            focus_y = (
                chart.bottom()
                - chart.height() * self.focus_values[i] / max_focus * 0.88
            )

            focus_points.append(
                (
                    x + bar_width / 2,
                    focus_y,
                )
            )

            painter.setPen(QColor(c.TEXT_SECONDARY))
            painter.drawText(
                QRectF(
                    x - 8,
                    chart.bottom() + 7,
                    bar_width + 16,
                    18,
                ),
                Qt.AlignmentFlag.AlignCenter,
                labels[i],
            )

        if focus_points:
            path = QPainterPath()
            path.moveTo(*focus_points[0])

            for point in focus_points[1:]:
                path.lineTo(*point)

            pen = QPen(QColor(c.PURPLE), 2.2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(c.PURPLE))

            for x, y in focus_points:
                painter.drawEllipse(
                    QRectF(
                        x - 3,
                        y - 3,
                        6,
                        6,
                    )
                )


class CompletionDonut(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percent = 0
        self.setMinimumSize(150, 150)

    def set_value(self, value):
        self.percent = max(0, min(100, int(value)))
        self.update()

    def paintEvent(self, event):
        c = ThemeManager.get().Colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        size = min(self.width(), self.height()) - 30
        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

        base = QPen(QColor("#202B3A"), 12)
        base.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(base)
        painter.drawArc(rect, 0, 360 * 16)

        accent = QPen(QColor(c.GREEN), 12)
        accent.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(accent)
        painter.drawArc(
            rect,
            90 * 16,
            -int(360 * 16 * self.percent / 100),
        )

        painter.setPen(QColor(c.TEXT))
        font = painter.font()
        font.setPointSize(22)
        font.setBold(True)
        painter.setFont(font)
        center_y = self.height() / 2

        painter.drawText(
            QRectF(
                0,
                center_y - 34,
                self.width(),
                38,
            ),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.percent}%",
        )

        painter.setPen(QColor(c.TEXT_SECONDARY))
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(
            QRectF(
                0,
                center_y + 5,
                self.width(),
                22,
            ),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            "Completion",
        )


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.task_manager = TaskManager()
        self.focus_manager = FocusManager()
        self.habit_manager = HabitManager()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollArea>QWidget>QWidget{background:transparent;}"
        )

        host = QWidget()
        host.setStyleSheet("background:transparent;")

        root = QVBoxLayout(host)
        root.setContentsMargins(
            Metrics.PAGE_X,
            Metrics.PAGE_Y,
            Metrics.PAGE_X,
            Metrics.PAGE_Y,
        )
        root.setSpacing(16)

        self.title = QLabel("Statistics")
        self.title.setObjectName("statisticsTitle")

        self.subtitle = QLabel(
            "See what your consistency is actually producing."
        )
        self.subtitle.setObjectName("statisticsSubtitle")

        root.addWidget(self.title)
        root.addWidget(self.subtitle)

        stats = QHBoxLayout()
        stats.setSpacing(10)

        self.total_stat = self._stat_card(
            "Total Tasks",
            "tasks",
            "tasks",
        )
        self.completed_stat = self._stat_card(
            "Completed",
            "check",
            "green",
        )
        self.pending_stat = self._stat_card(
            "Pending",
            "clock",
            "orange",
        )
        self.streak_stat = self._stat_card(
            "Current Streak",
            "flame",
            "purple",
        )

        for stat in (
            self.total_stat,
            self.completed_stat,
            self.pending_stat,
            self.streak_stat,
        ):
            stats.addWidget(stat["frame"], 1)

        root.addLayout(stats)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)

        self.performance_card = SurfaceCard(
            "Weekly Performance",
            "Blue bars = completed tasks · purple line = focus minutes.",
        )
        self.performance_card.setMinimumHeight(245)
        self.performance_period = HeaderPill("This Week")
        self.performance_card.set_header_action(
            self.performance_period
        )
        self.performance_chart = PerformanceChart()
        self.performance_card.body.addWidget(
            self.performance_chart,
            1,
        )

        self.completion_card = SurfaceCard(
            "Completion Rate",
            "Across all tasks currently in Flux.",
        )
        self.completion_card.setMinimumHeight(245)
        self.completion_donut = CompletionDonut()
        self.completion_card.body.addWidget(
            self.completion_donut,
            1,
            Qt.AlignmentFlag.AlignHCenter,
        )

        self.category_card = SurfaceCard(
            "Category Breakdown",
            "Where your current workload lives.",
        )
        self.category_card.setMinimumHeight(210)
        self.category_rows = QVBoxLayout()
        self.category_rows.setSpacing(8)
        self.category_card.body.addLayout(
            self.category_rows
        )

        self.consistency_card = SurfaceCard(
            "Consistency",
            "A compact view of focus, habits and momentum.",
        )
        self.consistency_card.setMinimumHeight(210)
        self.consistency_rows = QVBoxLayout()
        self.consistency_rows.setSpacing(8)
        self.consistency_card.body.addLayout(
            self.consistency_rows
        )

        grid.addWidget(
            self.performance_card,
            0,
            0,
        )
        grid.addWidget(
            self.completion_card,
            0,
            1,
        )
        grid.addWidget(
            self.category_card,
            1,
            0,
        )
        grid.addWidget(
            self.consistency_card,
            1,
            1,
        )

        root.addLayout(grid)
        root.addStretch(1)

        self.scroll.setWidget(host)
        outer.addWidget(self.scroll)

        self.apply_theme()
        self.refresh_stats()

    def _stat_card(
        self,
        label,
        icon_name,
        accent_key,
    ):
        frame = QFrame()
        frame.setObjectName("statisticsStat")

        row = QHBoxLayout(frame)
        row.setContentsMargins(13, 11, 13, 11)
        row.setSpacing(10)

        icon = IconCircle(
            icon_name,
            40,
        )

        text = QVBoxLayout()
        text.setSpacing(0)

        value = QLabel("0")
        value.setObjectName("statisticsStatValue")
        value.setProperty(
            "accent",
            accent_key,
        )

        caption = QLabel(label)
        caption.setObjectName("statisticsStatCaption")

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

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

    def _category_row(
        self,
        label,
        count,
        total,
        accent,
    ):
        wrap = QWidget()
        row = QVBoxLayout(wrap)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        top = QHBoxLayout()

        name = QLabel(label)
        name.setObjectName("statisticsRowLabel")

        value = QLabel(str(count))
        value.setObjectName("statisticsRowValue")

        top.addWidget(name)
        top.addStretch(1)
        top.addWidget(value)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setValue(
            round(count / total * 100)
            if total
            else 0
        )
        bar.setStyleSheet(
            f"""
            QProgressBar {{
                background:#202A39;
                border:none;
                border-radius:3px;
            }}
            QProgressBar::chunk {{
                background:{accent};
                border-radius:3px;
            }}
            """
        )

        row.addLayout(top)
        row.addWidget(bar)

        return wrap

    def _consistency_row(
        self,
        label,
        value,
        icon_name,
    ):
        frame = QFrame()
        frame.setObjectName("consistencyRow")

        row = QHBoxLayout(frame)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(9)

        icon = IconCircle(
            icon_name,
            34,
        )

        caption = QLabel(label)
        caption.setObjectName("statisticsRowLabel")

        metric = QLabel(value)
        metric.setObjectName("consistencyValue")

        row.addWidget(icon)
        row.addWidget(caption, 1)
        row.addWidget(metric)

        return frame

    def refresh_stats(self):
        tasks = self.task_manager.get_all_tasks()
        completed = [
            task
            for task in tasks
            if task.completed
        ]
        pending = [
            task
            for task in tasks
            if not task.completed
        ]

        total = len(tasks)
        completion_percent = (
            round(
                len(completed)
                / total
                * 100
            )
            if total
            else 0
        )

        streak = self.task_manager.calculate_streak()
        week = self.task_manager.get_week_completion()
        focus_week = self.focus_manager.get_week_minutes()
        focus_days = self.focus_manager.get_week_by_day()
        habit_percent = self.habit_manager.week_completion_percent()

        self.total_stat["value"].setText(
            str(total)
        )
        self.completed_stat["value"].setText(
            str(len(completed))
        )
        self.pending_stat["value"].setText(
            str(len(pending))
        )
        self.streak_stat["value"].setText(
            f"{streak}d"
        )

        self.performance_chart.set_values(
            week["counts"],
            focus_days,
        )
        self.completion_donut.set_value(
            completion_percent
        )

        self._clear_layout(
            self.category_rows
        )

        categories = Counter(
            (
                task.category
                or "General"
            )
            for task in tasks
        )

        palette = (
            ThemeManager.get().Colors.PRIMARY_LIGHT,
            ThemeManager.get().Colors.PURPLE,
            ThemeManager.get().Colors.GREEN,
            ThemeManager.get().Colors.ORANGE,
        )

        if categories:
            for index, (category, count) in enumerate(
                categories.most_common(4)
            ):
                self.category_rows.addWidget(
                    self._category_row(
                        category,
                        count,
                        total,
                        palette[
                            index
                            % len(palette)
                        ],
                    )
                )
        else:
            empty = QLabel(
                "Your category breakdown will appear after you add tasks."
            )
            empty.setObjectName(
                "statisticsMuted"
            )
            empty.setWordWrap(True)
            self.category_rows.addWidget(
                empty
            )

        self._clear_layout(
            self.consistency_rows
        )

        focus_text = self._format_minutes(
            focus_week
        )

        for label, value, icon in (
            (
                "Focus this week",
                focus_text,
                "timer",
            ),
            (
                "Habit completion",
                f"{habit_percent}%",
                "check",
            ),
            (
                "Task completion",
                f"{completion_percent}%",
                "chart",
            ),
            (
                "Current streak",
                f"{streak} days",
                "flame",
            ),
        ):
            self.consistency_rows.addWidget(
                self._consistency_row(
                    label,
                    value,
                    icon,
                )
            )

    @staticmethod
    def _format_minutes(minutes):
        hours, remainder = divmod(
            max(0, int(minutes or 0)),
            60,
        )
        if hours:
            return (
                f"{hours}h {remainder}m"
                if remainder
                else f"{hours}h"
            )
        return f"{remainder}m"

    def apply_theme(self):
        c = ThemeManager.get().Colors

        for card in (
            self.performance_card,
            self.completion_card,
            self.category_card,
            self.consistency_card,
        ):
            card.apply_theme()

        self.performance_period.apply_theme()

        for stat in (
            self.total_stat,
            self.completed_stat,
            self.pending_stat,
            self.streak_stat,
        ):
            stat["icon"].apply_theme()

        self.setStyleSheet(
            f"""
            QLabel#statisticsTitle {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:28px;
                font-weight:800;
            }}

            QLabel#statisticsSubtitle {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:12px;
            }}

            QFrame#statisticsStat {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:13px;
            }}

            QLabel#statisticsStatValue {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:20px;
                font-weight:800;
            }}

            QLabel#statisticsStatValue[accent="green"] {{
                color:{c.GREEN};
            }}

            QLabel#statisticsStatValue[accent="orange"] {{
                color:{c.ORANGE};
            }}

            QLabel#statisticsStatValue[accent="purple"] {{
                color:{c.PURPLE};
            }}

            QLabel#statisticsStatCaption,
            QLabel#statisticsMuted {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:9px;
            }}

            QLabel#statisticsRowLabel {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:10px;
            }}

            QLabel#statisticsRowValue,
            QLabel#consistencyValue {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:10px;
                font-weight:700;
            }}

            QFrame#consistencyRow {{
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:10px;
            }}
            """
        )

    def refresh_theme(self):
        self.apply_theme()
        self.refresh_stats()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(
            0,
            self.refresh_stats,
        )
