from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QScrollArea,
)

from themes.manager import ThemeManager
from ui.icons import IconGlyph
from utils.glass_effects import GlassFrame, apply_soft_shadow
from utils.habit_manager import HabitManager


class HabitProgressBar(QWidget):

    def __init__(
        self,
        completed,
        total,
        color
    ):

        super().__init__()

        self.completed = max(
            0,
            int(completed)
        )

        self.total = max(
            1,
            int(total)
        )

        self.color = color

        self.setFixedSize(
            104,
            10
        )


    def set_progress(
        self,
        completed,
        total=None
    ):

        self.completed = max(
            0,
            int(completed)
        )

        if total is not None:

            self.total = max(
                1,
                int(total)
            )

        self.update()


    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True
        )


        track = QRectF(
            0,
            1,
            self.width(),
            self.height() - 2
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                24
            )
        )

        painter.drawRoundedRect(
            track,
            4,
            4
        )


        ratio = min(
            1.0,
            self.completed / self.total
        )

        if ratio <= 0:

            return


        fill_width = max(
            8.0,
            track.width() * ratio
        )

        fill = QRectF(
            track.left(),
            track.top(),
            fill_width,
            track.height()
        )

        painter.setBrush(
            QColor(
                self.color
            )
        )

        painter.drawRoundedRect(
            fill,
            4,
            4
        )



class HabitDayButton(QPushButton):

    def __init__(self, checked=False):

        super().__init__()

        self.checked_visual = bool(
            checked
        )

        self.setFixedSize(
            34,
            34
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.icon = IconGlyph(
            "check",
            size=14,
            stroke_width=2.1,
            parent=self
        )

        self.icon.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self.apply_theme()


    def resizeEvent(self, event):

        self.icon.move(
            (self.width() - self.icon.width()) // 2,
            (self.height() - self.icon.height()) // 2
        )

        super().resizeEvent(
            event
        )


    def set_checked_visual(self, value):

        self.checked_visual = bool(
            value
        )

        self.apply_theme()


    def apply_theme(self):

        theme = ThemeManager.get()

        self.icon.setVisible(
            self.checked_visual
        )

        self.icon.setColor(
            "white"
        )

        background = (
            theme.Colors.PRIMARY
            if self.checked_visual
            else theme.Colors.GLASS
        )

        border = (
            theme.Colors.BORDER_ACTIVE
            if self.checked_visual
            else theme.Colors.BORDER
        )

        self.setStyleSheet(
            f"""
            QPushButton {{
                background:{background};
                border:1px solid {border};
                border-radius:9px;
            }}

            QPushButton:hover {{
                border-color:{theme.Colors.PRIMARY};
                background:{theme.Colors.GLASS_HOVER};
            }}
            """
        )


class HabitsPage(QWidget):

    ACCENT_COLORS = (
        "#5A7DFF",
        "#4BE8A5",
        "#A56EFF",
        "#FFC857",
        "#FF6B6B",
    )


    def __init__(self):

        super().__init__()

        self.manager = HabitManager()

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(
            18
        )


        header = QHBoxLayout()

        header.setSpacing(
            14
        )

        title_col = QVBoxLayout()

        title_col.setSpacing(
            2
        )

        self.title = QLabel(
            "Habits"
        )

        self.subtitle = QLabel(
            "Small actions. Every day."
        )

        title_col.addWidget(
            self.title
        )

        title_col.addWidget(
            self.subtitle
        )

        header.addLayout(
            title_col
        )

        header.addStretch()


        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "Add a new habit..."
        )

        self.name_input.setFixedWidth(
            260
        )

        self.name_input.returnPressed.connect(
            self.create_habit
        )


        self.add_button = QPushButton(
            "+  Add Habit"
        )

        self.add_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.add_button.clicked.connect(
            self.create_habit
        )

        header.addWidget(
            self.name_input
        )

        header.addWidget(
            self.add_button
        )

        root.addLayout(
            header
        )


        stats = QHBoxLayout()

        stats.setSpacing(
            16
        )

        self.active_card = self._stat_card(
            "Active Habits",
            "0",
            "tasks"
        )

        self.today_card = self._stat_card(
            "Done Today",
            "0",
            "check"
        )

        self.week_card = self._stat_card(
            "This Week",
            "0%",
            "chart"
        )

        self.streak_card = self._stat_card(
            "Best Streak",
            "0 Days",
            "flame"
        )

        for card in (
            self.active_card,
            self.today_card,
            self.week_card,
            self.streak_card,
        ):

            stats.addWidget(
                card,
                1
            )

        root.addLayout(
            stats
        )


        self.list_card = GlassFrame()

        self.list_card.setObjectName(
            "habitsListCard"
        )

        list_outer = QVBoxLayout(
            self.list_card
        )

        list_outer.setContentsMargins(
            20,
            18,
            20,
            18
        )

        list_outer.setSpacing(
            12
        )


        week_header = QHBoxLayout()

        week_header.setSpacing(
            7
        )

        self.week_label = QLabel(
            "This Week"
        )

        week_header.addWidget(
            self.week_label
        )

        week_header.addStretch()

        for text in (
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun",
        ):

            label = QLabel(
                text
            )

            label.setFixedWidth(
                34
            )

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            label.setObjectName(
                "habitDayLabel"
            )

            week_header.addWidget(
                label
            )

        week_header.addSpacing(
            45
        )

        list_outer.addLayout(
            week_header
        )


        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollArea>QWidget>QWidget{background:transparent;}"
        )


        self.list_host = QWidget()

        self.list_host.setStyleSheet(
            "background:transparent;"
        )

        self.list_layout = QVBoxLayout(
            self.list_host
        )

        self.list_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.list_layout.setSpacing(
            8
        )

        self.list_layout.addStretch(
            1
        )


        self.scroll.setWidget(
            self.list_host
        )

        list_outer.addWidget(
            self.scroll,
            1
        )

        root.addWidget(
            self.list_card,
            1
        )


        self.apply_theme()

        self.refresh_habits()


    def _stat_card(self, title, value, icon_name):

        card = GlassFrame()

        card.glass_radius = 18

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        layout.setSpacing(
            12
        )


        icon_wrap = QFrame()

        icon_wrap.setFixedSize(
            42,
            42
        )

        icon_wrap.setObjectName(
            "habitStatIcon"
        )

        icon_layout = QHBoxLayout(
            icon_wrap
        )

        icon_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        icon = IconGlyph(
            icon_name,
            size=22
        )

        icon_layout.addWidget(
            icon
        )


        text = QVBoxLayout()

        text.setSpacing(
            1
        )

        value_label = QLabel(
            value
        )

        title_label = QLabel(
            title
        )

        value_label.setObjectName(
            "habitStatValue"
        )

        title_label.setObjectName(
            "habitStatTitle"
        )

        text.addWidget(
            value_label
        )

        text.addWidget(
            title_label
        )


        layout.addWidget(
            icon_wrap
        )

        layout.addLayout(
            text,
            1
        )


        card._value_label = value_label

        card._title_label = title_label

        card._icon_wrap = icon_wrap

        card._icon = icon

        apply_soft_shadow(
            card
        )

        return card


    def create_habit(self):

        name = self.name_input.text().strip()

        if not name:
            return

        existing = self.manager.get_habits()

        color = self.ACCENT_COLORS[
            len(existing)
            % len(self.ACCENT_COLORS)
        ]

        self.manager.create_habit(
            name,
            color
        )

        self.name_input.clear()

        self.refresh_habits()


    def _clear_rows(self):

        while self.list_layout.count() > 1:

            item = self.list_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()


    def _toggle(self, habit_id, day, button):

        checked = self.manager.toggle_day(
            habit_id,
            day
        )

        button.set_checked_visual(
            checked
        )

        self.refresh_habits()


    def _delete(self, habit_id):

        self.manager.delete_habit(
            habit_id
        )

        self.refresh_habits()


    def _habit_row(self, habit):

        theme = ThemeManager.get()

        row = QFrame()

        row.setObjectName(
            "habitRow"
        )

        layout = QHBoxLayout(
            row
        )

        layout.setContentsMargins(
            14,
            10,
            10,
            10
        )

        layout.setSpacing(
            7
        )


        name = QLabel(
            habit["name"]
        )

        name.setObjectName(
            "habitName"
        )

        name.setMinimumWidth(
            170
        )


        done = sum(
            1
            for _day, completed in habit["week"]
            if completed
        )

        progress = HabitProgressBar(
            completed=done,
            total=7,
            color=theme.Colors.PRIMARY
        )


        progress_text = QLabel(
            f"{done}/7"
        )

        progress_text.setObjectName(
            "habitProgressText"
        )

        progress_text.setFixedWidth(
            26
        )

        progress_text.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )


        layout.addWidget(
            name,
            1
        )

        layout.addWidget(
            progress
        )

        layout.addWidget(
            progress_text
        )

        layout.addSpacing(
            6
        )


        for day, completed in habit["week"]:

            button = HabitDayButton(
                completed
            )

            button.clicked.connect(
                lambda _checked=False, hid=habit["id"], d=day, b=button:
                self._toggle(
                    hid,
                    d,
                    b
                )
            )

            layout.addWidget(
                button
            )


        delete = QPushButton(
            "×"
        )

        delete.setObjectName(
            "habitDelete"
        )

        delete.setFixedSize(
            34,
            34
        )

        delete.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        delete.clicked.connect(
            lambda _checked=False, hid=habit["id"]:
            self._delete(
                hid
            )
        )

        layout.addWidget(
            delete
        )


        return row


    def refresh_habits(self):

        self._clear_rows()

        habits = self.manager.habits_with_week()

        if not habits:

            empty = QLabel(
                "No habits yet. Add one above and start your week."
            )

            empty.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty.setObjectName(
                "habitEmpty"
            )

            self.list_layout.insertWidget(
                0,
                empty
            )

        else:

            for habit in habits:

                self.list_layout.insertWidget(
                    self.list_layout.count() - 1,
                    self._habit_row(
                        habit
                    )
                )


        week = self.manager.week_days()

        self.week_label.setText(
            (
                f"{week[0].strftime('%b %d')} – "
                f"{week[-1].strftime('%b %d')}"
            )
        )

        self._update_stats()


    def _update_stats(self):

        habits = self.manager.get_habits()

        self.active_card._value_label.setText(
            str(
                len(habits)
            )
        )

        self.today_card._value_label.setText(
            str(
                self.manager.completed_today()
            )
        )

        self.week_card._value_label.setText(
            f"{self.manager.weekly_completion()}%"
        )

        self.streak_card._value_label.setText(
            f"{self.manager.best_streak()} Days"
        )


    def apply_theme(self):

        theme = ThemeManager.get()

        self.title.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:32px;
            font-weight:800;
            background:transparent;
            """
        )

        self.subtitle.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT_SECONDARY};
            font-size:15px;
            background:transparent;
            """
        )

        self.name_input.setStyleSheet(
            f"""
            QLineEdit {{
                background:{theme.Colors.GLASS};
                color:{theme.Colors.TEXT};
                border:1px solid {theme.Colors.BORDER};
                border-radius:12px;
                padding:10px 14px;
            }}

            QLineEdit:focus {{
                border-color:{theme.Colors.PRIMARY};
            }}
            """
        )

        self.add_button.setStyleSheet(
            f"""
            QPushButton {{
                background:{theme.Colors.PRIMARY};
                color:white;
                border:1px solid {theme.Colors.BORDER_ACTIVE};
                border-radius:12px;
                padding:10px 16px;
                font-weight:700;
            }}

            QPushButton:hover {{
                background:{theme.Colors.BORDER_ACTIVE};
            }}
            """
        )

        self.list_card.setStyleSheet(
            f"""
            QFrame#habitsListCard {{
                background:{theme.Colors.GLASS};
                border:1px solid {theme.Colors.BORDER};
                border-radius:20px;
            }}
            """
        )

        self.week_label.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:15px;
            font-weight:700;
            background:transparent;
            border:none;
            """
        )

        self.setStyleSheet(
            f"""
            QLabel#habitDayLabel {{
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:10px;
                background:transparent;
                border:none;
            }}

            QFrame#habitRow {{
                background:{theme.Colors.SURFACE};
                border:1px solid {theme.Colors.BORDER};
                border-radius:14px;
            }}

            QFrame#habitRow:hover {{
                background:{theme.Colors.SURFACE_ALT};
            }}

            QLabel#habitName {{
                color:{theme.Colors.TEXT};
                font-size:13px;
                font-weight:600;
                background:transparent;
                border:none;
            }}

            QLabel#habitProgressText {{
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:10px;
                font-weight:600;
                background:transparent;
                border:none;
            }}

            QLabel#habitEmpty {{
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:14px;
                background:transparent;
                border:none;
                padding:36px;
            }}

            QPushButton#habitDelete {{
                background:transparent;
                color:{theme.Colors.TEXT_SECONDARY};
                border:none;
                border-radius:8px;
                font-size:18px;
            }}

            QPushButton#habitDelete:hover {{
                background:{theme.Colors.GLASS_HOVER};
                color:{theme.Colors.RED};
            }}

            QFrame#habitStatIcon {{
                background:{theme.Colors.GLASS_HOVER};
                border:1px solid {theme.Colors.BORDER};
                border-radius:12px;
            }}

            QLabel#habitStatValue {{
                color:{theme.Colors.TEXT};
                font-size:22px;
                font-weight:800;
                background:transparent;
                border:none;
            }}

            QLabel#habitStatTitle {{
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:10px;
                background:transparent;
                border:none;
            }}
            """
        )

        for card in (
            self.active_card,
            self.today_card,
            self.week_card,
            self.streak_card,
        ):

            card._icon.setColor(
                theme.Colors.PRIMARY
            )

            card.update()


    def refresh_theme(self):

        self.apply_theme()

        self.refresh_habits()


    def showEvent(self, event):

        super().showEvent(
            event
        )

        QTimer.singleShot(
            0,
            self.refresh_habits
        )
