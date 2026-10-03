from PySide6.QtCore import Qt, QDate, Signal, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QGridLayout,
)

from utils.task_manager import TaskManager
from ui.taskcard import TaskCard
from ui.add_task_dialog import AddTaskDialog
from ui.edit_task_dialog import EditTaskDialog
from utils.glass_effects import GlassFrame
from themes.manager import ThemeManager


class CalendarDayButton(QPushButton):

    selected = Signal(QDate)


    def __init__(self, parent=None):

        super().__init__(parent)

        self.date = QDate.currentDate()
        self.in_current_month = True
        self.is_selected = False
        self.is_today = False
        self.marker = None

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setMinimumWidth(
            52
        )

        self.setMinimumHeight(
            50
        )

        self.setMaximumHeight(
            56
        )

        self.clicked.connect(
            self._emit_selected
        )


    def _emit_selected(self):

        self.selected.emit(
            self.date
        )


    def configure(
        self,
        date,
        current_month,
        selected_date,
        marker=None
    ):

        self.date = date

        self.in_current_month = (
            date.month() == current_month
        )

        self.is_selected = (
            date == selected_date
        )

        self.is_today = (
            date == QDate.currentDate()
        )

        self.marker = marker

        self.setToolTip(
            date.toString(
                "dddd, MMMM d"
            )
        )

        self.update()


    def paintEvent(self, event):

        theme = ThemeManager.get()

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True
        )


        rect = QRectF(
            3,
            3,
            self.width() - 6,
            self.height() - 6
        )


        if self.is_selected:

            fill = QColor(
                theme.Colors.PRIMARY
            )

            border = QColor(
                theme.Colors.BORDER_ACTIVE
            )

        elif self.is_today:

            fill = QColor(
                theme.Colors.GLASS_HOVER
            )

            border = QColor(
                theme.Colors.PRIMARY
            )

        else:

            fill = QColor(
                theme.Colors.SURFACE
            )

            fill.setAlpha(
                115
                if self.in_current_month
                else 42
            )

            border = QColor(
                theme.Colors.BORDER
            )

            border.setAlpha(
                95
                if self.in_current_month
                else 35
            )


        painter.setPen(
            QPen(
                border,
                1
            )
        )

        painter.setBrush(
            fill
        )

        painter.drawRoundedRect(
            rect,
            11,
            11
        )


        if self.is_selected:

            text_color = QColor(
                "white"
            )

        elif self.in_current_month:

            text_color = QColor(
                theme.Colors.TEXT
            )

        else:

            text_color = QColor(
                theme.Colors.TEXT_SECONDARY
            )

            text_color.setAlpha(
                105
            )


        painter.setPen(
            text_color
        )

        font = painter.font()

        font.setFamily(
            "Helvetica"
        )

        font.setPointSize(
            10
        )

        font.setBold(
            self.is_selected
            or self.is_today
        )

        painter.setFont(
            font
        )

        painter.drawText(
            QRectF(
                0,
                7,
                self.width(),
                28
            ),
            Qt.AlignmentFlag.AlignCenter,
            str(
                self.date.day()
            )
        )


        if self.marker:

            marker_color = QColor(
                theme.Colors.GREEN
                if self.marker == "done"
                else theme.Colors.PRIMARY
            )

            if self.is_selected:

                marker_color = QColor(
                    "white"
                )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                marker_color
            )

            painter.drawEllipse(
                QRectF(
                    self.width() / 2 - 2.5,
                    self.height() - 12,
                    5,
                    5
                )
            )


class FluxCalendarWidget(QWidget):

    dateSelected = Signal(QDate)

    currentPageChanged = Signal(int, int)


    def __init__(self, parent=None):

        super().__init__(parent)

        today = QDate.currentDate()

        self._selected_date = today
        self._year = today.year()
        self._month = today.month()
        self._markers = {}


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
            14
        )


        nav = QHBoxLayout()

        nav.setSpacing(
            8
        )


        self.prev_button = QPushButton(
            "‹"
        )

        self.next_button = QPushButton(
            "›"
        )

        self.today_button = QPushButton(
            "Today"
        )

        self.month_label = QLabel()

        self.month_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )


        for button in (
            self.prev_button,
            self.next_button,
            self.today_button,
        ):

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )


        self.prev_button.clicked.connect(
            self.previous_month
        )

        self.next_button.clicked.connect(
            self.next_month
        )

        self.today_button.clicked.connect(
            self.go_today
        )


        nav.addWidget(
            self.prev_button
        )

        nav.addWidget(
            self.next_button
        )

        nav.addStretch()

        nav.addWidget(
            self.month_label
        )

        nav.addStretch()

        nav.addWidget(
            self.today_button
        )

        root.addLayout(
            nav
        )


        weekday_row = QHBoxLayout()

        weekday_row.setSpacing(
            6
        )


        self.weekday_labels = []

        for day in (
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun",
        ):

            label = QLabel(
                day
            )

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.weekday_labels.append(
                label
            )

            weekday_row.addWidget(
                label,
                1
            )

        root.addLayout(
            weekday_row
        )


        self.grid = QGridLayout()

        self.grid.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.grid.setHorizontalSpacing(
            6
        )

        self.grid.setVerticalSpacing(
            6
        )


        self.day_buttons = []

        for index in range(42):

            button = CalendarDayButton(
                self
            )

            button.selected.connect(
                self._select_date
            )

            self.day_buttons.append(
                button
            )

            self.grid.addWidget(
                button,
                index // 7,
                index % 7
            )

        root.addLayout(
            self.grid
        )

        root.addStretch(
            1
        )


        self.apply_theme()

        self._render_month()


    def selectedDate(self):

        return self._selected_date


    def setSelectedDate(self, date):

        if not date.isValid():

            return

        page_changed = (
            self._year != date.year()
            or self._month != date.month()
        )

        self._selected_date = date

        self._year = date.year()
        self._month = date.month()

        self._render_month()

        if page_changed:

            self.currentPageChanged.emit(
                self._year,
                self._month
            )


    def set_markers(self, markers):

        self._markers = dict(
            markers
            or {}
        )

        self._render_month()


    def _select_date(self, date):

        self.setSelectedDate(
            date
        )

        self.dateSelected.emit(
            date
        )


    def previous_month(self):

        first = QDate(
            self._year,
            self._month,
            1
        ).addMonths(
            -1
        )

        self._year = first.year()
        self._month = first.month()

        self._render_month()

        self.currentPageChanged.emit(
            self._year,
            self._month
        )


    def next_month(self):

        first = QDate(
            self._year,
            self._month,
            1
        ).addMonths(
            1
        )

        self._year = first.year()
        self._month = first.month()

        self._render_month()

        self.currentPageChanged.emit(
            self._year,
            self._month
        )


    def go_today(self):

        today = QDate.currentDate()

        self.setSelectedDate(
            today
        )

        self.dateSelected.emit(
            today
        )


    def _render_month(self):

        first = QDate(
            self._year,
            self._month,
            1
        )

        offset = (
            first.dayOfWeek()
            - 1
        )

        start = first.addDays(
            -offset
        )


        self.month_label.setText(
            first.toString(
                "MMMM yyyy"
            )
        )


        for index, button in enumerate(
            self.day_buttons
        ):

            date = start.addDays(
                index
            )

            marker = self._markers.get(
                date.toString(
                    "yyyy-MM-dd"
                )
            )

            button.configure(
                date=date,
                current_month=self._month,
                selected_date=self._selected_date,
                marker=marker
            )


    def apply_theme(self):

        theme = ThemeManager.get()

        self.month_label.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:19px;
            font-weight:800;
            background:transparent;
            border:none;
            """
        )

        for label in self.weekday_labels:

            label.setStyleSheet(
                f"""
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:10px;
                font-weight:700;
                background:transparent;
                border:none;
                """
            )


        nav_style = f"""
        QPushButton {{
            background:{theme.Colors.GLASS};
            color:{theme.Colors.TEXT_SECONDARY};
            border:1px solid {theme.Colors.BORDER};
            border-radius:10px;
            padding:8px 12px;
            font-weight:700;
        }}

        QPushButton:hover {{
            color:{theme.Colors.TEXT};
            background:{theme.Colors.GLASS_HOVER};
            border-color:{theme.Colors.BORDER_ACTIVE};
        }}
        """

        self.prev_button.setStyleSheet(
            nav_style
        )

        self.next_button.setStyleSheet(
            nav_style
        )

        self.today_button.setStyleSheet(
            nav_style
        )


        for button in self.day_buttons:

            button.update()


class CalendarPage(QWidget):

    def __init__(self):

        super().__init__()

        self.task_manager = TaskManager()


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


        header_row = QHBoxLayout()

        title_col = QVBoxLayout()

        title_col.setSpacing(
            2
        )

        self.title = QLabel(
            "Calendar"
        )

        self.subtitle = QLabel(
            "Plan your days and deadlines."
        )

        title_col.addWidget(
            self.title
        )

        title_col.addWidget(
            self.subtitle
        )

        header_row.addLayout(
            title_col
        )

        header_row.addStretch()


        self.add_button = QPushButton(
            "+  Add Task"
        )

        self.add_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.add_button.clicked.connect(
            self.open_add_task
        )

        header_row.addWidget(
            self.add_button
        )

        root.addLayout(
            header_row
        )


        split_row = QHBoxLayout()

        split_row.setSpacing(
            18
        )


        self.card = GlassFrame()

        self.card.setObjectName(
            "calendarCard"
        )

        card_layout = QVBoxLayout(
            self.card
        )

        card_layout.setContentsMargins(
            20,
            18,
            20,
            20
        )


        self.calendar = FluxCalendarWidget()

        self.calendar.dateSelected.connect(
            self.date_selected
        )

        self.calendar.currentPageChanged.connect(
            lambda _year, _month:
            self.mark_task_dates()
        )

        card_layout.addWidget(
            self.calendar
        )

        split_row.addWidget(
            self.card,
            5
        )


        self.day_panel = GlassFrame()

        self.day_panel.setObjectName(
            "calendarDayPanel"
        )

        day_layout = QVBoxLayout(
            self.day_panel
        )

        day_layout.setContentsMargins(
            20,
            18,
            20,
            20
        )

        day_layout.setSpacing(
            10
        )


        self.selected_label = QLabel()

        self.selected_label.setObjectName(
            "calendarSelectedDate"
        )

        self.day_count_label = QLabel()

        self.day_count_label.setObjectName(
            "calendarDayCount"
        )

        day_layout.addWidget(
            self.selected_label
        )

        day_layout.addWidget(
            self.day_count_label
        )


        divider = QFrame()

        divider.setFixedHeight(
            1
        )

        divider.setObjectName(
            "calendarDivider"
        )

        day_layout.addWidget(
            divider
        )


        self.day_scroll = QScrollArea()

        self.day_scroll.setWidgetResizable(
            True
        )

        self.day_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.day_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.day_scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollArea>QWidget>QWidget{background:transparent;}"
        )


        self.day_content = QWidget()

        self.day_content.setStyleSheet(
            "background:transparent;"
        )

        self.day_task_layout = QVBoxLayout(
            self.day_content
        )

        self.day_task_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.day_task_layout.setSpacing(
            8
        )

        self.day_scroll.setWidget(
            self.day_content
        )

        day_layout.addWidget(
            self.day_scroll,
            1
        )


        split_row.addWidget(
            self.day_panel,
            4
        )


        root.addLayout(
            split_row,
            1
        )


        self.apply_theme()

        self.mark_task_dates()

        self.date_selected(
            QDate.currentDate()
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


        self.add_button.setStyleSheet(
            f"""
            QPushButton {{
                background:{theme.Colors.PRIMARY};
                color:white;
                border:1px solid {theme.Colors.BORDER_ACTIVE};
                border-radius:12px;
                padding:10px 18px;
                font-weight:700;
            }}

            QPushButton:hover {{
                background:{theme.Colors.BORDER_ACTIVE};
            }}
            """
        )


        self.card.setStyleSheet(
            f"""
            QFrame#calendarCard {{
                background:{theme.Colors.GLASS};
                border-radius:20px;
                border:1px solid {theme.Colors.BORDER};
            }}
            """
        )


        self.day_panel.setStyleSheet(
            f"""
            QFrame#calendarDayPanel {{
                background:{theme.Colors.GLASS};
                border-radius:20px;
                border:1px solid {theme.Colors.BORDER};
            }}
            """
        )


        self.selected_label.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:19px;
            font-weight:800;
            background:transparent;
            border:none;
            """
        )


        self.day_count_label.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT_SECONDARY};
            font-size:11px;
            background:transparent;
            border:none;
            """
        )


        divider = self.day_panel.findChild(
            QFrame,
            "calendarDivider"
        )

        if divider:

            divider.setStyleSheet(
                f"""
                background:{theme.Colors.BORDER};
                border:none;
                """
            )


        self.calendar.apply_theme()


    def refresh_theme(self):

        self.apply_theme()

        self.mark_task_dates()

        self.date_selected(
            self.calendar.selectedDate()
        )


    def showEvent(self, event):

        super().showEvent(
            event
        )

        self.mark_task_dates()

        self.date_selected(
            self.calendar.selectedDate()
        )


    def mark_task_dates(self):

        tasks = self.task_manager.get_all_tasks()

        by_date = {}

        for task in tasks:

            if not task.task_date:

                continue

            by_date.setdefault(
                task.task_date,
                []
            ).append(
                task
            )


        markers = {}

        for date_string, day_tasks in by_date.items():

            markers[date_string] = (
                "done"
                if all(
                    task.completed
                    for task in day_tasks
                )
                else "pending"
            )


        self.calendar.set_markers(
            markers
        )


    def date_selected(self, date):

        self.calendar.setSelectedDate(
            date
        )

        self.selected_label.setText(
            date.toString(
                "dddd, MMMM d"
            )
        )


        while self.day_task_layout.count():

            item = self.day_task_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:

                widget.hide()

                widget.deleteLater()


        date_string = date.toString(
            "yyyy-MM-dd"
        )


        tasks = [
            task
            for task in self.task_manager.get_all_tasks()
            if task.task_date == date_string
        ]


        self.day_count_label.setText(
            (
                "No tasks"
                if not tasks
                else (
                    "1 task"
                    if len(tasks) == 1
                    else f"{len(tasks)} tasks"
                )
            )
        )


        theme = ThemeManager.get()


        if not tasks:

            empty = QFrame()

            empty.setObjectName(
                "calendarEmpty"
            )

            empty_layout = QVBoxLayout(
                empty
            )

            empty_layout.setContentsMargins(
                16,
                28,
                16,
                28
            )

            empty_layout.setSpacing(
                5
            )


            empty_title = QLabel(
                "Nothing planned"
            )

            empty_title.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty_subtitle = QLabel(
                "This day is clear."
            )

            empty_subtitle.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )


            empty_title.setStyleSheet(
                f"""
                color:{theme.Colors.TEXT};
                font-size:14px;
                font-weight:700;
                background:transparent;
                border:none;
                """
            )

            empty_subtitle.setStyleSheet(
                f"""
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:11px;
                background:transparent;
                border:none;
                """
            )


            empty_layout.addWidget(
                empty_title
            )

            empty_layout.addWidget(
                empty_subtitle
            )

            empty.setStyleSheet(
                f"""
                QFrame#calendarEmpty {{
                    background:{theme.Colors.SURFACE};
                    border:1px dashed {theme.Colors.BORDER};
                    border-radius:14px;
                }}
                """
            )

            self.day_task_layout.addWidget(
                empty
            )

        else:

            for task in tasks:

                card = TaskCard(
                    task.title,
                    task.time,
                    task.priority,
                    task.category,
                    task.completed,
                    color=task.color,
                    important=task.important
                )


                card.checkedChanged.connect(
                    lambda checked, tid=task.id:
                    self.on_task_completed(
                        tid,
                        checked
                    )
                )


                card.deleteClicked.connect(
                    lambda tid=task.id:
                    self.on_delete_task(
                        tid
                    )
                )


                card.editClicked.connect(
                    lambda t=task:
                    self.open_edit_task(
                        t
                    )
                )


                self.day_task_layout.addWidget(
                    card
                )


        self.day_task_layout.addStretch()


    def open_add_task(self):

        dialog = AddTaskDialog()

        dialog.dateInput.setDate(
            self.calendar.selectedDate()
        )

        dialog.taskCreated.connect(
            self.on_task_created
        )

        dialog.exec()


    def on_task_created(
        self,
        title,
        time,
        priority,
        category,
        date,
        description,
        color,
        reminder,
        repeat,
        important
    ):

        self.task_manager.create_task(
            title=title,
            time=time,
            task_date=date,
            priority=priority,
            category=category,
            description=description,
            color=color,
            reminder=reminder,
            repeat=repeat,
            important=important
        )

        self.mark_task_dates()

        self.date_selected(
            self.calendar.selectedDate()
        )


    def open_edit_task(self, task):

        dialog = EditTaskDialog(
            task
        )

        dialog.taskUpdated.connect(
            self.on_task_updated
        )

        dialog.exec()


    def on_task_updated(
        self,
        task_id,
        title,
        time,
        priority,
        category,
        task_date,
        description,
        color,
        reminder,
        repeat,
        important
    ):

        self.task_manager.edit_task(
            task_id=task_id,
            title=title,
            time=time,
            task_date=task_date,
            priority=priority,
            category=category,
            description=description,
            color=color,
            reminder=reminder,
            repeat=repeat,
            important=important
        )

        self.mark_task_dates()

        self.date_selected(
            self.calendar.selectedDate()
        )


    def on_task_completed(self, task_id, checked):

        self.task_manager.complete_task(
            task_id,
            checked
        )

        self.mark_task_dates()

        self.date_selected(
            self.calendar.selectedDate()
        )


    def on_delete_task(self, task_id):

        self.task_manager.remove_task(
            task_id
        )

        self.mark_task_dates()

        self.date_selected(
            self.calendar.selectedDate()
        )
