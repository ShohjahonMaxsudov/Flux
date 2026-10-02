from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDateEdit,
    QFrame,
    QProgressBar,
    QScrollArea
)

from themes.manager import ThemeManager
from utils.glass_effects import GlassFrame
from utils.milestone_manager import MilestoneManager
from utils.task_manager import TaskManager


class MilestonesPage(QWidget):

    def __init__(self):

        super().__init__()

        self.manager = MilestoneManager()

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        self.title = QLabel("Milestones")
        self.subtitle = QLabel("Turn big goals into visible progress.")

        root.addWidget(self.title)
        root.addWidget(self.subtitle)

        summary = QHBoxLayout()
        summary.setSpacing(12)

        self.activeCard, self.activeValue = self._summary_card("ACTIVE")
        self.doneCard, self.doneValue = self._summary_card("COMPLETED")
        self.streakCard, self.streakValue = self._summary_card("TASK STREAK")

        for card in (self.activeCard, self.doneCard, self.streakCard):
            summary.addWidget(card, 1)

        root.addLayout(summary)

        self.createCard = GlassFrame()
        self.createCard.setObjectName("milestoneCreateCard")

        createLayout = QHBoxLayout(self.createCard)
        createLayout.setContentsMargins(18, 14, 18, 14)
        createLayout.setSpacing(10)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("New milestone...")

        self.targetInput = QSpinBox()
        self.targetInput.setRange(1, 100000)
        self.targetInput.setValue(100)
        self.targetInput.setPrefix("Target ")

        self.dateInput = QDateEdit(QDate.currentDate().addMonths(1))
        self.dateInput.setCalendarPopup(True)
        self.dateInput.setDisplayFormat("dd MMM yyyy")

        self.addButton = QPushButton("+ Add Milestone")
        self.addButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.addButton.clicked.connect(self._create_milestone)
        self.nameInput.returnPressed.connect(self._create_milestone)

        createLayout.addWidget(self.nameInput, 1)
        createLayout.addWidget(self.targetInput)
        createLayout.addWidget(self.dateInput)
        createLayout.addWidget(self.addButton)

        root.addWidget(self.createCard)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.listWidget = QWidget()
        self.listLayout = QVBoxLayout(self.listWidget)
        self.listLayout.setContentsMargins(0, 0, 6, 0)
        self.listLayout.setSpacing(10)
        self.listLayout.addStretch(1)

        self.scroll.setWidget(self.listWidget)
        root.addWidget(self.scroll, 1)

        self.apply_theme()
        self.load_milestones()


    def _summary_card(self, caption):

        card = QFrame()
        card.setObjectName("milestoneSummaryCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(2)

        value = QLabel("0")
        value.setObjectName("milestoneMetricValue")

        label = QLabel(caption)
        label.setObjectName("milestoneMetricCaption")

        layout.addWidget(value)
        layout.addWidget(label)

        return card, value


    def _create_milestone(self):

        title = self.nameInput.text().strip()

        if not title:
            self.nameInput.setFocus()
            return

        self.manager.create(
            title=title,
            target=self.targetInput.value(),
            due_date=self.dateInput.date().toString("yyyy-MM-dd"),
            color=ThemeManager.get().Colors.PRIMARY
        )

        self.nameInput.clear()
        self.targetInput.setValue(100)
        self.dateInput.setDate(QDate.currentDate().addMonths(1))

        self.load_milestones()


    def _set_progress(self, milestone, delta):

        self.manager.set_progress(
            milestone["id"],
            int(milestone["progress"]) + delta
        )

        self.load_milestones()


    def _delete(self, milestone_id):

        self.manager.delete(milestone_id)
        self.load_milestones()


    def _clear_cards(self):

        while self.listLayout.count() > 1:

            item = self.listLayout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()


    def _milestone_card(self, milestone):

        theme = ThemeManager.get()

        card = QFrame()
        card.setObjectName("milestoneCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        top = QHBoxLayout()

        title = QLabel(milestone["title"])
        title.setObjectName("milestoneCardTitle")

        target = max(1, int(milestone["target"]))
        progress = max(0, min(target, int(milestone["progress"])))
        percent = round((progress / target) * 100)

        status = QLabel(
            "Complete"
            if progress >= target
            else f"{progress} / {target}"
        )
        status.setObjectName("milestoneCardStatus")

        top.addWidget(title, 1)
        top.addWidget(status)

        bar = QProgressBar()
        bar.setObjectName("milestoneProgress")
        bar.setRange(0, 100)
        bar.setValue(percent)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)

        bottom = QHBoxLayout()

        due = milestone.get("due_date", "") or "No due date"
        dueLabel = QLabel(
            due if due == "No due date" else f"Due {due}"
        )
        dueLabel.setObjectName("milestoneDue")

        minus = QPushButton("-10")
        plus = QPushButton("+10")
        delete = QPushButton("Delete")

        for button in (minus, plus):
            button.setObjectName("milestoneStepButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        delete.setObjectName("milestoneDeleteButton")
        delete.setCursor(Qt.CursorShape.PointingHandCursor)

        minus.clicked.connect(
            lambda _checked=False, m=milestone:
                self._set_progress(m, -10)
        )
        plus.clicked.connect(
            lambda _checked=False, m=milestone:
                self._set_progress(m, 10)
        )
        delete.clicked.connect(
            lambda _checked=False, mid=milestone["id"]:
                self._delete(mid)
        )

        bottom.addWidget(dueLabel, 1)
        bottom.addWidget(minus)
        bottom.addWidget(plus)
        bottom.addWidget(delete)

        layout.addLayout(top)
        layout.addWidget(bar)
        layout.addLayout(bottom)

        return card


    def load_milestones(self):

        milestones = self.manager.all()

        active = sum(
            1
            for item in milestones
            if int(item["progress"]) < int(item["target"])
        )

        self.activeValue.setText(str(active))
        self.doneValue.setText(str(len(milestones) - active))

        taskManager = TaskManager()
        self.streakValue.setText(str(taskManager.calculate_streak()))
        taskManager.close()

        self._clear_cards()

        if not milestones:

            empty = QLabel("No milestones yet — add your first big goal above.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setObjectName("milestoneEmpty")
            self.listLayout.insertWidget(0, empty)

        else:

            for milestone in milestones:
                self.listLayout.insertWidget(
                    self.listLayout.count() - 1,
                    self._milestone_card(milestone)
                )

        self.apply_theme()


    def showEvent(self, event):

        super().showEvent(event)
        self.load_milestones()


    def apply_theme(self):

        theme = ThemeManager.get()
        c = theme.Colors

        self.setStyleSheet(
            f"""
            QLabel#milestoneMetricValue {{
                color:{c.TEXT};
                font-size:24px;
                font-weight:800;
                background:transparent;
                border:none;
            }}

            QLabel#milestoneMetricCaption {{
                color:{c.TEXT_SECONDARY};
                font-size:10px;
                font-weight:700;
                background:transparent;
                border:none;
            }}

            QFrame#milestoneSummaryCard,
            QFrame#milestoneCard {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:16px;
            }}

            QLabel#milestoneCardTitle {{
                color:{c.TEXT};
                font-size:17px;
                font-weight:750;
                background:transparent;
                border:none;
            }}

            QLabel#milestoneCardStatus,
            QLabel#milestoneDue,
            QLabel#milestoneEmpty {{
                color:{c.TEXT_SECONDARY};
                font-size:12px;
                background:transparent;
                border:none;
            }}

            QProgressBar#milestoneProgress {{
                background:{c.SURFACE_ALT};
                border:none;
                border-radius:4px;
            }}

            QProgressBar#milestoneProgress::chunk {{
                background:{c.PRIMARY};
                border-radius:4px;
            }}

            QPushButton#milestoneStepButton,
            QPushButton#milestoneDeleteButton {{
                background:{c.SURFACE_ALT};
                color:{c.TEXT_SECONDARY};
                border:1px solid {c.BORDER};
                border-radius:9px;
                padding:7px 11px;
                font-weight:650;
            }}

            QPushButton#milestoneStepButton:hover {{
                color:{c.TEXT};
                border-color:{c.BORDER_ACTIVE};
            }}

            QPushButton#milestoneDeleteButton:hover {{
                color:{c.ERROR};
                border-color:{c.ERROR};
            }}
            """
        )

        self.title.setStyleSheet(
            f"color:{c.TEXT}; font-size:32px; font-weight:800; background:transparent;"
        )

        self.subtitle.setStyleSheet(
            f"color:{c.TEXT_SECONDARY}; font-size:15px; background:transparent;"
        )

        inputStyle = f"""
        QLineEdit, QSpinBox, QDateEdit {{
            background:{c.SURFACE_ALT};
            color:{c.TEXT};
            border:1px solid {c.BORDER};
            border-radius:10px;
            padding:9px 11px;
        }}
        QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {{
            border-color:{c.BORDER_ACTIVE};
        }}
        """

        self.nameInput.setStyleSheet(inputStyle)
        self.targetInput.setStyleSheet(inputStyle)
        self.dateInput.setStyleSheet(inputStyle)

        self.addButton.setStyleSheet(
            f"""
            QPushButton {{
                background:{c.PRIMARY};
                color:{c.BACKGROUND};
                border:none;
                border-radius:10px;
                padding:10px 15px;
                font-weight:800;
            }}
            """
        )


    def refresh_theme(self):

        self.apply_theme()
        self.load_milestones()
