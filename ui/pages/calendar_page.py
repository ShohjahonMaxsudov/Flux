from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCalendarWidget,
    QFrame,
    QScrollArea
)

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QFont

from utils.task_manager import TaskManager
from ui.taskcard import TaskCard
from ui.add_task_dialog import AddTaskDialog
from ui.edit_task_dialog import EditTaskDialog
from utils.glass_effects import GlassFrame
from themes.manager import ThemeManager


class CalendarPage(QWidget):

    # Previously this page was pure decoration: a QCalendarWidget with
    # no TaskManager import at all, no marked dates, no connection to
    # the database whatsoever. Selecting a date only updated a label.
    # This version marks every date that has tasks, lists the selected
    # day's tasks (with working complete/edit/delete), and lets you add
    # a task straight onto the selected date.

    def __init__(self):

        super().__init__()

        self.task_manager = TaskManager()

        self._marked_dates = set()


        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        root.setSpacing(18)


        headerRow = QHBoxLayout()

        titleCol = QVBoxLayout()

        titleCol.setSpacing(2)

        self.title = QLabel("Calendar")

        self.subtitle = QLabel("Plan your days and deadlines.")

        titleCol.addWidget(self.title)

        titleCol.addWidget(self.subtitle)

        headerRow.addLayout(titleCol)

        headerRow.addStretch()


        self.addButton = QPushButton("+  Add Task")

        self.addButton.setCursor(Qt.PointingHandCursor)

        self.addButton.clicked.connect(self.open_add_task)

        headerRow.addWidget(self.addButton)

        root.addLayout(headerRow)



        splitRow = QHBoxLayout()

        splitRow.setSpacing(18)


        self.card = GlassFrame()

        self.card.setObjectName(
            "calendarCard"
        )

        cardLayout = QVBoxLayout(self.card)

        cardLayout.setContentsMargins(20, 20, 20, 20)


        self.calendar = QCalendarWidget()

        self.calendar.setGridVisible(True)

        self.calendar.setSelectedDate(QDate.currentDate())

        self.calendar.clicked.connect(self.date_selected)

        self.calendar.currentPageChanged.connect(
            lambda year, month: self.mark_task_dates()
        )

        cardLayout.addWidget(self.calendar)

        splitRow.addWidget(self.card, 3)



        self.dayPanel = GlassFrame()

        self.dayPanel.setObjectName(
            "calendarDayPanel"
        )

        dayLayout = QVBoxLayout(self.dayPanel)

        dayLayout.setContentsMargins(20, 20, 20, 20)

        dayLayout.setSpacing(10)


        self.selectedLabel = QLabel()

        dayLayout.addWidget(self.selectedLabel)


        self.dayScroll = QScrollArea()

        self.dayScroll.setWidgetResizable(True)

        self.dayScroll.setFrameShape(QFrame.NoFrame)

        self.dayScroll.setStyleSheet(
            "QScrollArea{ background:transparent; border:none; }"
            "QScrollArea > QWidget > QWidget{ background:transparent; }"
        )


        self.dayContent = QWidget()

        self.dayContent.setStyleSheet("background:transparent;")

        self.dayTaskLayout = QVBoxLayout(self.dayContent)

        self.dayTaskLayout.setContentsMargins(0, 0, 0, 0)

        self.dayTaskLayout.setSpacing(8)

        self.dayScroll.setWidget(self.dayContent)

        dayLayout.addWidget(self.dayScroll, 1)


        splitRow.addWidget(self.dayPanel, 2)


        root.addLayout(splitRow, 1)


        self.apply_theme()

        self.mark_task_dates()

        self.date_selected(QDate.currentDate())



    def apply_theme(self):

        theme = ThemeManager.get()


        self.title.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:32px; font-weight:800; background:transparent;"
        )


        self.subtitle.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:15px; background:transparent;"
        )


        self.addButton.setStyleSheet(
            f"""
            QPushButton{{

                background:{theme.Colors.PRIMARY};

                color:white;

                border-radius:12px;

                padding:10px 18px;

                font-weight:bold;

            }}

            QPushButton:hover{{

                background:{theme.Colors.BORDER_ACTIVE};

            }}
            """
        )


        for frame in (self.card, self.dayPanel):

            frame.setStyleSheet(
                f"""
                QFrame#{frame.objectName()}{{

                    background:{theme.Colors.GLASS};

                    border-radius:20px;

                    border:1px solid {theme.Colors.BORDER};

                }}
                """
            )


        self.selectedLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:18px; font-weight:700; background:transparent; border:none;"
        )


        self.calendar.setStyleSheet(
            f"""
            QCalendarWidget QWidget{{

                background:{theme.Colors.SURFACE_ALT};

                color:{theme.Colors.TEXT};

            }}


            QCalendarWidget QToolButton{{

                color:{theme.Colors.TEXT};

                background:transparent;

                font-size:16px;

                font-weight:bold;

            }}


            QCalendarWidget QMenu{{

                background:{theme.Colors.SURFACE};

                color:{theme.Colors.TEXT};

            }}


            QCalendarWidget QAbstractItemView{{

                background:{theme.Colors.SURFACE_ALT};

                color:{theme.Colors.TEXT};

                selection-background-color:{theme.Colors.PRIMARY};

                selection-color:white;

            }}
            """
        )



    def refresh_theme(self):

        self.apply_theme()

        self.mark_task_dates()

        self.date_selected(self.calendar.selectedDate())



    def showEvent(self, event):

        super().showEvent(event)

        self.mark_task_dates()

        self.date_selected(self.calendar.selectedDate())



    # -------------------------
    # MARK DATES WITH TASKS
    # -------------------------

    def mark_task_dates(self):

        theme = ThemeManager.get()


        blank = QTextCharFormat()

        for d in self._marked_dates:

            self.calendar.setDateTextFormat(d, blank)

        self._marked_dates.clear()


        tasks = self.task_manager.get_all_tasks()


        by_date = {}

        for task in tasks:

            if not task.task_date:
                continue

            d = QDate.fromString(task.task_date, "yyyy-MM-dd")

            if not d.isValid():
                continue

            by_date.setdefault(d, []).append(task)


        for d, day_tasks in by_date.items():

            fmt = QTextCharFormat()

            fmt.setFontWeight(QFont.Bold)

            all_done = all(t.completed for t in day_tasks)

            fmt.setForeground(
                QColor(
                    theme.Colors.GREEN
                    if all_done
                    else theme.Colors.PRIMARY
                )
            )

            self.calendar.setDateTextFormat(d, fmt)

            self._marked_dates.add(d)



    # -------------------------
    # SELECTED DAY
    # -------------------------

    def date_selected(self, date):

        self.calendar.setSelectedDate(date)

        self.selectedLabel.setText(
            date.toString("dddd, MMMM d")
        )


        while self.dayTaskLayout.count():

            item = self.dayTaskLayout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.hide()

                widget.deleteLater()


        date_str = date.toString("yyyy-MM-dd")

        tasks = [
            task
            for task in self.task_manager.get_all_tasks()
            if task.task_date == date_str
        ]


        theme = ThemeManager.get()


        if not tasks:

            empty = QLabel(
                "Nothing on the calendar for this day"
            )

            empty.setStyleSheet(
                f"color:{theme.Colors.TEXT_SECONDARY}; font-size:14px; background:transparent; padding:8px; border:none;"
            )

            self.dayTaskLayout.addWidget(empty)


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
                    self.on_task_completed(tid, checked)
                )


                card.deleteClicked.connect(
                    lambda tid=task.id:
                    self.on_delete_task(tid)
                )


                card.editClicked.connect(
                    lambda t=task:
                    self.open_edit_task(t)
                )


                self.dayTaskLayout.addWidget(card)


        self.dayTaskLayout.addStretch()



    # -------------------------
    # ADD / EDIT / COMPLETE / DELETE
    # -------------------------

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

        self.date_selected(self.calendar.selectedDate())



    def open_edit_task(self, task):

        dialog = EditTaskDialog(task)

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

        self.date_selected(self.calendar.selectedDate())



    def on_task_completed(self, task_id, checked):

        self.task_manager.complete_task(task_id, checked)

        self.mark_task_dates()

        self.date_selected(self.calendar.selectedDate())



    def on_delete_task(self, task_id):

        self.task_manager.remove_task(task_id)

        self.mark_task_dates()

        self.date_selected(self.calendar.selectedDate())
