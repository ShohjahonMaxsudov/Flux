from PySide6.QtCore import Signal, QDate, QTime
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTimeEdit,
    QComboBox,
    QTextEdit,
    QDateEdit,
    QCheckBox,
    QScrollArea
)

from themes.manager import ThemeManager


CATEGORIES = [
    "General",
    "Study",
    "Work",
    "Fitness",
    "Health",
    "Coding",
    "Personal"
]

PRIORITIES = [
    "Low",
    "Normal",
    "High"
]

COLORS = [
    "#5A7DFF",
    "#4BE8A5",
    "#FFC857",
    "#FF5D5D",
    "#A56EFF"
]

REMINDERS = [
    "None",
    "5 minutes before",
    "15 minutes before",
    "30 minutes before"
]

REPEATS = [
    "Never",
    "Daily",
    "Weekly",
    "Monthly"
]


class EditTaskDialog(QDialog):

    # Same field set, same order as AddTaskDialog.taskCreated, with the
    # task id prepended so Dashboard knows which row to update. Editing
    # used to only carry title/time/priority/category (and crashed on
    # save besides, since Database.update_task didn't exist) — every
    # field Create Task collects can now be changed here too.

    taskUpdated = Signal(
        int,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        bool
    )


    def __init__(
        self,
        task
    ):

        super().__init__()

        self.task = task


        self.setWindowTitle(
            "Edit Task"
        )


        self.resize(
            520,
            760
        )


        self.build_ui()

        self.apply_theme()

        self.load_task()



    def build_ui(self):

        main = QVBoxLayout(
            self
        )


        main.setContentsMargins(
            0,
            0,
            0,
            0
        )



        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QScrollArea.NoFrame
        )

        scroll.setStyleSheet(
            "QScrollArea{ background:transparent; border:none; }"
            "QScrollArea > QWidget > QWidget{ background:transparent; }"
        )



        content = QWidget()

        content.setStyleSheet(
            "background:transparent;"
        )


        layout = QVBoxLayout(
            content
        )


        layout.setContentsMargins(
            32,
            28,
            32,
            28
        )


        layout.setSpacing(
            14
        )



        self.title = QLabel(
            "Edit Task"
        )


        layout.addWidget(
            self.title
        )



        layout.addWidget(
            QLabel("Task Name")
        )


        self.nameInput = QLineEdit()


        self.nameInput.setPlaceholderText(
            "What needs to be done?"
        )


        layout.addWidget(
            self.nameInput
        )



        layout.addWidget(
            QLabel("Description")
        )


        self.descriptionInput = QTextEdit()


        self.descriptionInput.setPlaceholderText(
            "Add notes, details..."
        )


        layout.addWidget(
            self.descriptionInput
        )



        layout.addWidget(
            QLabel("Date")
        )


        self.dateInput = QDateEdit()


        self.dateInput.setCalendarPopup(
            True
        )


        layout.addWidget(
            self.dateInput
        )



        layout.addWidget(
            QLabel("Time")
        )


        self.timeInput = QTimeEdit()


        self.timeInput.setDisplayFormat(
            "HH:mm"
        )


        layout.addWidget(
            self.timeInput
        )



        layout.addWidget(
            QLabel("Category")
        )


        self.categoryInput = QComboBox()


        self.categoryInput.addItems(
            CATEGORIES
        )


        layout.addWidget(
            self.categoryInput
        )



        layout.addWidget(
            QLabel("Priority")
        )


        self.priorityInput = QComboBox()


        self.priorityInput.addItems(
            PRIORITIES
        )


        layout.addWidget(
            self.priorityInput
        )



        layout.addWidget(
            QLabel("Color")
        )


        self.colorInput = QComboBox()


        self.colorInput.addItems(
            COLORS
        )


        layout.addWidget(
            self.colorInput
        )



        layout.addWidget(
            QLabel("Reminder")
        )


        self.reminderInput = QComboBox()


        self.reminderInput.addItems(
            REMINDERS
        )


        layout.addWidget(
            self.reminderInput
        )



        layout.addWidget(
            QLabel("Repeat")
        )


        self.repeatInput = QComboBox()


        self.repeatInput.addItems(
            REPEATS
        )


        layout.addWidget(
            self.repeatInput
        )



        self.importantInput = QCheckBox(
            "Important Task ★"
        )


        layout.addWidget(
            self.importantInput
        )



        layout.addSpacing(
            20
        )



        self.saveButton = QPushButton(
            "Save Changes"
        )


        self.saveButton.clicked.connect(
            self.save_task
        )


        layout.addWidget(
            self.saveButton
        )


        layout.addStretch()



        scroll.setWidget(
            content
        )


        main.addWidget(
            scroll
        )



    def load_task(self):

        task = self.task


        self.nameInput.setText(
            task.title
        )


        self.descriptionInput.setPlainText(
            task.description
        )


        if task.task_date:

            date = QDate.fromString(
                task.task_date,
                "yyyy-MM-dd"
            )


            self.dateInput.setDate(
                date
                if date.isValid()
                else QDate.currentDate()
            )


        else:

            self.dateInput.setDate(
                QDate.currentDate()
            )


        if task.time:

            try:

                hour, minute = map(
                    int,
                    task.time.split(":")
                )


                self.timeInput.setTime(
                    QTime(
                        hour,
                        minute
                    )
                )


            except ValueError:

                pass


        if self.categoryInput.findText(task.category) == -1:

            self.categoryInput.addItem(
                task.category
            )


        self.categoryInput.setCurrentText(
            task.category
        )


        if self.priorityInput.findText(task.priority) == -1:

            self.priorityInput.addItem(
                task.priority
            )


        self.priorityInput.setCurrentText(
            task.priority
        )


        if self.colorInput.findText(task.color) == -1:

            self.colorInput.addItem(
                task.color
            )


        self.colorInput.setCurrentText(
            task.color
        )


        if self.reminderInput.findText(task.reminder) == -1:

            self.reminderInput.addItem(
                task.reminder
            )


        self.reminderInput.setCurrentText(
            task.reminder
        )


        if self.repeatInput.findText(task.repeat) == -1:

            self.repeatInput.addItem(
                task.repeat
            )


        self.repeatInput.setCurrentText(
            task.repeat
        )


        self.importantInput.setChecked(
            bool(task.important)
        )



    def apply_theme(self):

        theme = ThemeManager.get()



        self.setStyleSheet(
            f"""
            QDialog{{

                background:{theme.Colors.BACKGROUND};

            }}


            QLabel{{

                color:{theme.Colors.TEXT};

                background:transparent;

                font-size:14px;

            }}


            QLineEdit,
            QTextEdit,
            QDateEdit,
            QTimeEdit,
            QComboBox{{

                background:{theme.Colors.SURFACE_ALT};

                color:{theme.Colors.TEXT};

                border:1px solid {theme.Colors.BORDER};

                border-radius:12px;

                padding:10px;

            }}


            QTextEdit{{

                min-height:90px;

            }}


            QComboBox QAbstractItemView{{

                background:{theme.Colors.SURFACE};

                color:{theme.Colors.TEXT};

                selection-background-color:{theme.Colors.PRIMARY};

            }}


            QPushButton{{

                background:{theme.Colors.PRIMARY};

                color:white;

                border-radius:14px;

                padding:14px;

                font-size:15px;

                font-weight:700;

            }}


            QPushButton:hover{{

                background:{theme.Colors.BORDER_ACTIVE};

            }}


            QCheckBox{{

                color:{theme.Colors.TEXT};

                font-size:14px;

            }}

            """
        )



        self.title.setStyleSheet(
            f"""
            QLabel{{

                color:{theme.Colors.TEXT};

                font-size:28px;

                font-weight:900;

            }}

            """
        )



    def save_task(self):

        title = self.nameInput.text().strip()


        if not title:

            self.nameInput.setStyleSheet(
                self.nameInput.styleSheet() +
                "QLineEdit{border:1px solid #FF5D5D;}"
            )

            self.nameInput.setPlaceholderText(
                "Task name can't be empty"
            )

            return



        self.taskUpdated.emit(

            self.task.id,

            title,

            self.timeInput.time().toString(
                "HH:mm"
            ),

            self.priorityInput.currentText(),

            self.categoryInput.currentText(),

            self.dateInput.date().toString(
                "yyyy-MM-dd"
            ),

            self.descriptionInput.toPlainText(),

            self.colorInput.currentText(),

            self.reminderInput.currentText(),

            self.repeatInput.currentText(),

            self.importantInput.isChecked()

        )


        self.accept()
