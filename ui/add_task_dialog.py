from PySide6.QtCore import Signal, QDate
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



class AddTaskDialog(QDialog):

    taskCreated = Signal(
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


    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "Create Task"
        )


        self.resize(
            520,
            760
        )


        self.build_ui()

        self.apply_theme()



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
            "Create New Task"
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


        self.dateInput.setDate(
            QDate.currentDate()
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
            [
                "General",
                "Study",
                "Work",
                "Fitness",
                "Health",
                "Coding",
                "Personal"
            ]
        )


        layout.addWidget(
            self.categoryInput
        )



        layout.addWidget(
            QLabel("Priority")
        )


        self.priorityInput = QComboBox()


        self.priorityInput.addItems(
            [
                "Low",
                "Normal",
                "High"
            ]
        )


        layout.addWidget(
            self.priorityInput
        )



        layout.addWidget(
            QLabel("Color")
        )


        self.colorInput = QComboBox()


        self.colorInput.addItems(
            [
                "#5A7DFF",
                "#4BE8A5",
                "#FFC857",
                "#FF5D5D",
                "#A56EFF"
            ]
        )


        layout.addWidget(
            self.colorInput
        )



        layout.addWidget(
            QLabel("Reminder")
        )


        self.reminderInput = QComboBox()


        self.reminderInput.addItems(
            [
                "None",
                "5 minutes before",
                "15 minutes before",
                "30 minutes before"
            ]
        )


        layout.addWidget(
            self.reminderInput
        )



        layout.addWidget(
            QLabel("Repeat")
        )


        self.repeatInput = QComboBox()


        self.repeatInput.addItems(
            [
                "Never",
                "Daily",
                "Weekly",
                "Monthly"
            ]
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



        self.createButton = QPushButton(
            "Create Task"
        )


        self.createButton.clicked.connect(
            self.create_task
        )


        layout.addWidget(
            self.createButton
        )


        layout.addStretch()



        scroll.setWidget(
            content
        )


        main.addWidget(
            scroll
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



    def create_task(self):

        title = self.nameInput.text().strip()


        if not title:
            return



        self.taskCreated.emit(

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