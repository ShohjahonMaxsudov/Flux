from PySide6.QtCore import QDate, QTime, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.design_system import GradientButton, SurfaceCard


CATEGORIES = (
    "General",
    "Study",
    "Work",
    "Fitness",
    "Health",
    "Coding",
    "Personal",
)

PRIORITIES = (
    "Low",
    "Normal",
    "High",
)

REMINDERS = (
    "None",
    "5 minutes before",
    "15 minutes before",
    "30 minutes before",
)

REPEATS = (
    "Never",
    "Daily",
    "Weekly",
    "Monthly",
)


class TaskFormDialog(QDialog):
    """Shared v3 task editor so Create/Edit never drift visually."""

    def __init__(self, title, subtitle, action_text, task=None, parent=None):
        super().__init__(parent)

        self.task = task
        self._action_text = action_text

        self.setWindowTitle(title)
        self.resize(650, 720)
        self.setMinimumSize(560, 600)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        shell = QFrame()
        shell.setObjectName("taskDialogShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(24, 22, 24, 20)
        shell_layout.setSpacing(14)

        header = QVBoxLayout()
        header.setSpacing(3)

        self.titleLabel = QLabel(title)
        self.titleLabel.setObjectName("taskDialogTitle")
        self.subtitleLabel = QLabel(subtitle)
        self.subtitleLabel.setObjectName("taskDialogSubtitle")

        header.addWidget(self.titleLabel)
        header.addWidget(self.subtitleLabel)
        shell_layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollArea>QWidget>QWidget{background:transparent;}"
        )

        host = QWidget()
        host.setStyleSheet("background:transparent;")
        content = QVBoxLayout(host)
        content.setContentsMargins(0, 0, 4, 0)
        content.setSpacing(12)

        self.mainCard = SurfaceCard("Task")
        self.nameInput = QLineEdit()
        self.nameInput.setObjectName("taskFormInput")
        self.nameInput.setPlaceholderText("What needs to be done?")

        self.descriptionInput = QTextEdit()
        self.descriptionInput.setObjectName("taskFormDescription")
        self.descriptionInput.setPlaceholderText("Add a short note or context…")
        self.descriptionInput.setFixedHeight(104)

        self.mainCard.body.addWidget(self._field_label("Task name"))
        self.mainCard.body.addWidget(self.nameInput)
        self.mainCard.body.addWidget(self._field_label("Description"))
        self.mainCard.body.addWidget(self.descriptionInput)

        content.addWidget(self.mainCard)

        self.detailsCard = SurfaceCard(
            "Schedule & details",
            "Keep the essentials visible without turning task creation into a form maze.",
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.dateInput = QDateEdit(QDate.currentDate())
        self.dateInput.setObjectName("taskFormInput")
        self.dateInput.setCalendarPopup(True)
        self.dateInput.setDisplayFormat("dd MMM yyyy")

        self.timeInput = QTimeEdit(QTime(9, 0))
        self.timeInput.setObjectName("taskFormInput")
        self.timeInput.setDisplayFormat("HH:mm")

        self.categoryInput = QComboBox()
        self.categoryInput.setObjectName("taskFormInput")
        self.categoryInput.addItems(CATEGORIES)

        self.priorityInput = QComboBox()
        self.priorityInput.setObjectName("taskFormInput")
        self.priorityInput.addItems(PRIORITIES)
        self.priorityInput.setCurrentText("Normal")

        grid.addWidget(self._field_wrap("Date", self.dateInput), 0, 0)
        grid.addWidget(self._field_wrap("Time", self.timeInput), 0, 1)
        grid.addWidget(self._field_wrap("Category", self.categoryInput), 1, 0)
        grid.addWidget(self._field_wrap("Priority", self.priorityInput), 1, 1)

        self.detailsCard.body.addLayout(grid)
        content.addWidget(self.detailsCard)

        self.optionsCard = SurfaceCard("Options")

        options_grid = QGridLayout()
        options_grid.setHorizontalSpacing(10)
        options_grid.setVerticalSpacing(10)

        self.reminderInput = QComboBox()
        self.reminderInput.setObjectName("taskFormInput")
        self.reminderInput.addItems(REMINDERS)

        self.repeatInput = QComboBox()
        self.repeatInput.setObjectName("taskFormInput")
        self.repeatInput.addItems(REPEATS)

        options_grid.addWidget(self._field_wrap("Reminder", self.reminderInput), 0, 0)
        options_grid.addWidget(self._field_wrap("Repeat", self.repeatInput), 0, 1)

        self.optionsCard.body.addLayout(options_grid)

        self.importantInput = QCheckBox("Mark as important")
        self.importantInput.setObjectName("taskImportant")
        self.optionsCard.body.addWidget(self.importantInput)

        content.addWidget(self.optionsCard)
        content.addStretch(1)

        scroll.setWidget(host)
        shell_layout.addWidget(scroll, 1)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch(1)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setObjectName("taskDialogCancel")
        self.cancelButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancelButton.clicked.connect(self.reject)

        self.actionButton = GradientButton(action_text, "check")
        self.actionButton.setMinimumWidth(150)

        footer.addWidget(self.cancelButton)
        footer.addWidget(self.actionButton)
        shell_layout.addLayout(footer)

        root.addWidget(shell)

        # Kept as compatibility data, deliberately not exposed in the UI.
        self._color_value = (
            getattr(task, "color", None)
            or ThemeManager.get().Colors.PRIMARY
        )

        self.apply_theme()

        if task is not None:
            self.load_task(task)

    def _field_label(self, text):
        label = QLabel(text)
        label.setObjectName("taskFormLabel")
        return label

    def _field_wrap(self, label_text, widget):
        frame = QWidget()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self._field_label(label_text))
        layout.addWidget(widget)
        return frame

    def load_task(self, task):
        self.nameInput.setText(task.title or "")
        self.descriptionInput.setPlainText(task.description or "")

        date = QDate.fromString(task.task_date or "", "yyyy-MM-dd")
        self.dateInput.setDate(date if date.isValid() else QDate.currentDate())

        if task.time:
            parsed = QTime.fromString(task.time, "HH:mm")
            if parsed.isValid():
                self.timeInput.setTime(parsed)

        for combo, value in (
            (self.categoryInput, task.category or "General"),
            (self.priorityInput, task.priority or "Normal"),
            (self.reminderInput, task.reminder or "None"),
            (self.repeatInput, task.repeat or "Never"),
        ):
            if combo.findText(value) == -1:
                combo.addItem(value)
            combo.setCurrentText(value)

        self.importantInput.setChecked(bool(task.important))
        self._color_value = task.color or ThemeManager.get().Colors.PRIMARY

    def values(self):
        return {
            "title": self.nameInput.text().strip(),
            "time": self.timeInput.time().toString("HH:mm"),
            "priority": self.priorityInput.currentText(),
            "category": self.categoryInput.currentText(),
            "task_date": self.dateInput.date().toString("yyyy-MM-dd"),
            "description": self.descriptionInput.toPlainText().strip(),
            "color": self._color_value,
            "reminder": self.reminderInput.currentText(),
            "repeat": self.repeatInput.currentText(),
            "important": self.importantInput.isChecked(),
        }

    def validate(self):
        if self.nameInput.text().strip():
            self.nameInput.setProperty("invalid", False)
            self.nameInput.style().unpolish(self.nameInput)
            self.nameInput.style().polish(self.nameInput)
            return True

        self.nameInput.setProperty("invalid", True)
        self.nameInput.setPlaceholderText("Give the task a name")
        self.nameInput.style().unpolish(self.nameInput)
        self.nameInput.style().polish(self.nameInput)
        self.nameInput.setFocus()
        return False

    def apply_theme(self):
        c = ThemeManager.get().Colors

        for card in (self.mainCard, self.detailsCard, self.optionsCard):
            card.apply_theme()

        self.actionButton.apply_theme()

        self.setStyleSheet(
            f"""
            QDialog {{
                background:#07101B;
            }}
            QFrame#taskDialogShell {{
                background:{c.BACKGROUND};
                border:1px solid rgba(130,155,190,0.18);
                border-radius:18px;
            }}
            QLabel#taskDialogTitle {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:28px;
                font-weight:800;
            }}
            QLabel#taskDialogSubtitle {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:11px;
            }}
            QLabel#taskFormLabel {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:10px;
                font-weight:600;
            }}
            QLineEdit#taskFormInput,
            QTextEdit#taskFormDescription,
            QDateEdit#taskFormInput,
            QTimeEdit#taskFormInput,
            QComboBox#taskFormInput {{
                color:{c.TEXT};
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:10px;
                padding:9px 11px;
                font-size:11px;
            }}
            QLineEdit#taskFormInput:focus,
            QTextEdit#taskFormDescription:focus,
            QDateEdit#taskFormInput:focus,
            QTimeEdit#taskFormInput:focus,
            QComboBox#taskFormInput:focus {{
                border-color:{c.BORDER_ACTIVE};
            }}
            QLineEdit#taskFormInput[invalid="true"] {{
                border-color:{c.ERROR};
            }}
            QComboBox QAbstractItemView {{
                color:{c.TEXT};
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                selection-background-color:{c.PRIMARY};
                selection-color:white;
            }}
            QCheckBox#taskImportant {{
                color:{c.TEXT};
                background:transparent;
                border:none;
                font-size:11px;
                spacing:8px;
            }}
            QPushButton#taskDialogCancel {{
                color:{c.TEXT_SECONDARY};
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:10px;
                padding:10px 18px;
                font-size:11px;
                font-weight:700;
            }}
            QPushButton#taskDialogCancel:hover {{
                color:{c.TEXT};
                border-color:{c.BORDER_ACTIVE};
            }}
            """
        )
