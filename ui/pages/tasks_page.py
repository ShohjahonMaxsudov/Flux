from datetime import datetime

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.edit_task_dialog import EditTaskDialog
from utils.focus_manager import FocusManager
from utils.task_manager import TaskManager


class TasksPage(QWidget):

    def __init__(self):

        super().__init__()

        self.task_manager = TaskManager()
        self.focus_manager = FocusManager()

        self.selected_task = None
        self.current_filter = "All"

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 4, 6, 6)
        root.setSpacing(16)

        header = QHBoxLayout()

        heading = QVBoxLayout()
        heading.setSpacing(2)

        self.eyebrow = QLabel("Good evening")
        self.eyebrow.setObjectName("tasksEyebrow")

        self.hero = QLabel("Tasks keep progress alive.")
        self.hero.setObjectName("tasksHero")

        heading.addWidget(self.eyebrow)
        heading.addWidget(self.hero)

        right = QVBoxLayout()

        self.search = QLineEdit()
        self.search.setObjectName("tasksSearch")
        self.search.setPlaceholderText("Search tasks…")
        self.search.setFixedWidth(310)
        self.search.textChanged.connect(self.load_tasks)

        self.dateLabel = QLabel()
        self.dateLabel.setObjectName("tasksDate")

        right.addWidget(
            self.search,
            0,
            Qt.AlignmentFlag.AlignRight
        )
        right.addWidget(
            self.dateLabel,
            0,
            Qt.AlignmentFlag.AlignRight
        )

        header.addLayout(heading, 1)
        header.addLayout(right)

        root.addLayout(header)

        toolbar = QFrame()
        toolbar.setObjectName("tasksToolbar")

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 8, 8, 8)
        toolbar_layout.setSpacing(5)

        self.tabButtons = {}

        for key in ("All", "Today", "Upcoming", "Completed"):

            button = QPushButton(key)
            button.setObjectName("taskTab")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, k=key:
                    self.set_filter(k)
            )

            toolbar_layout.addWidget(button)
            self.tabButtons[key] = button

        toolbar_layout.addStretch(1)

        sort_label = QLabel("Sort")
        sort_label.setObjectName("toolbarLabel")

        self.sort = QComboBox()
        self.sort.setObjectName("tasksSort")
        self.sort.addItems(
            (
                "Priority",
                "Due Date",
                "Newest",
                "Title A-Z",
            )
        )
        self.sort.currentTextChanged.connect(self.load_tasks)

        toolbar_layout.addWidget(sort_label)
        toolbar_layout.addWidget(self.sort)

        root.addWidget(toolbar)

        body = QHBoxLayout()
        body.setSpacing(16)

        self.taskScroll = QScrollArea()
        self.taskScroll.setWidgetResizable(True)
        self.taskScroll.setFrameShape(QFrame.Shape.NoFrame)
        self.taskScroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.taskHost = QWidget()

        self.taskLayout = QVBoxLayout(self.taskHost)
        self.taskLayout.setContentsMargins(0, 0, 6, 0)
        self.taskLayout.setSpacing(14)
        self.taskLayout.addStretch(1)

        self.taskScroll.setWidget(self.taskHost)

        body.addWidget(self.taskScroll, 1)

        self.side = QWidget()
        self.side.setFixedWidth(340)

        side_layout = QVBoxLayout(self.side)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(14)

        self.summaryCard = QFrame()
        self.summaryCard.setObjectName("taskSideCard")

        summary_layout = QVBoxLayout(self.summaryCard)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(10)

        summary_title = QLabel("Productivity Summary")
        summary_title.setObjectName("sideTitle")

        summary_layout.addWidget(summary_title)

        self.completedSummary = self._summary_row(
            "Completed Today",
            "check"
        )
        self.upcomingSummary = self._summary_row(
            "Upcoming Tasks",
            "calendar"
        )
        self.focusSummary = self._summary_row(
            "Focus Time",
            "chart"
        )

        for row in (
            self.completedSummary,
            self.upcomingSummary,
            self.focusSummary,
        ):
            summary_layout.addWidget(row["frame"])

        side_layout.addWidget(self.summaryCard)

        self.quickCard = QFrame()
        self.quickCard.setObjectName("taskSideCard")

        quick = QVBoxLayout(self.quickCard)
        quick.setContentsMargins(16, 16, 16, 16)
        quick.setSpacing(10)

        quick_title = QLabel("Quick Add Task")
        quick_title.setObjectName("sideTitle")

        self.quickTitle = QLineEdit()
        self.quickTitle.setObjectName("quickTitle")
        self.quickTitle.setPlaceholderText("What do you want to get done?")
        self.quickTitle.returnPressed.connect(self.quick_add)

        quick_meta = QHBoxLayout()

        self.quickDate = QDateEdit(QDate.currentDate())
        self.quickDate.setObjectName("quickInput")
        self.quickDate.setCalendarPopup(True)
        self.quickDate.setDisplayFormat("dd MMM")

        self.quickPriority = QComboBox()
        self.quickPriority.setObjectName("quickInput")
        self.quickPriority.addItems(("Low", "Normal", "High"))
        self.quickPriority.setCurrentText("Normal")

        self.quickCategory = QComboBox()
        self.quickCategory.setObjectName("quickInput")
        self.quickCategory.addItems(
            (
                "General",
                "Study",
                "Work",
                "Fitness",
                "Health",
                "Coding",
                "Personal",
            )
        )

        quick_meta.addWidget(self.quickDate)
        quick_meta.addWidget(self.quickPriority)
        quick_meta.addWidget(self.quickCategory)

        self.quickButton = QPushButton("+  Add Task")
        self.quickButton.setObjectName("quickAddButton")
        self.quickButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quickButton.clicked.connect(self.quick_add)

        quick.addWidget(quick_title)
        quick.addWidget(self.quickTitle)
        quick.addLayout(quick_meta)
        quick.addWidget(self.quickButton)

        side_layout.addWidget(self.quickCard)

        self.detailCard = QFrame()
        self.detailCard.setObjectName("taskSideCard")

        details = QVBoxLayout(self.detailCard)
        details.setContentsMargins(16, 16, 16, 16)
        details.setSpacing(10)

        detail_title = QLabel("Task Details")
        detail_title.setObjectName("sideTitle")

        self.detailBody = QVBoxLayout()
        self.detailBody.setSpacing(8)

        details.addWidget(detail_title)
        details.addLayout(self.detailBody)

        side_layout.addWidget(self.detailCard, 1)

        body.addWidget(self.side)

        root.addLayout(body, 1)

        self.apply_theme()
        self.set_filter("All")
        self.load_tasks()


    def _summary_row(self, label, icon):

        frame = QFrame()
        frame.setObjectName("summaryRow")

        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)

        icon_label = QLabel(
            "✓"
            if icon == "check"
            else ("▣" if icon == "calendar" else "▥")
        )
        icon_label.setObjectName("summaryIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(42, 42)

        text = QVBoxLayout()
        text.setSpacing(0)

        value = QLabel("0")
        value.setObjectName("summaryValue")

        caption = QLabel(label)
        caption.setObjectName("summaryCaption")

        text.addWidget(value)
        text.addWidget(caption)

        row.addWidget(icon_label)
        row.addLayout(text, 1)

        return {
            "frame": frame,
            "value": value,
            "caption": caption,
        }


    def set_filter(self, key):

        self.current_filter = key

        for button_key, button in self.tabButtons.items():
            button.setProperty(
                "active",
                button_key == key
            )
            button.style().unpolish(button)
            button.style().polish(button)

        self.load_tasks()


    def _clear_task_rows(self):

        while self.taskLayout.count() > 1:

            item = self.taskLayout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()


    def _matches_filter(self, task):

        today = datetime.now().strftime("%Y-%m-%d")

        if self.current_filter == "Completed":
            return task.completed

        if task.completed:
            return self.current_filter == "All"

        if self.current_filter == "Today":
            return not task.task_date or task.task_date == today

        if self.current_filter == "Upcoming":
            return bool(task.task_date and task.task_date > today)

        return True


    def _sort_tasks(self, tasks):

        mode = self.sort.currentText()

        if mode == "Priority":
            return sorted(
                tasks,
                key=lambda t: (
                    t.completed,
                    t.priority_order,
                    t.task_date or "9999-99-99",
                )
            )

        if mode == "Due Date":
            return sorted(
                tasks,
                key=lambda t: (
                    t.completed,
                    t.task_date or "9999-99-99",
                )
            )

        if mode == "Title A-Z":
            return sorted(
                tasks,
                key=lambda t: t.title.lower()
            )

        return list(reversed(tasks))


    def load_tasks(self):

        self.dateLabel.setText(
            datetime.now().strftime("%a, %b %d, %Y")
        )

        self._clear_task_rows()

        tasks = self.task_manager.get_all_tasks()

        text = self.search.text().strip().lower()

        if text:
            tasks = [
                task
                for task in tasks
                if (
                    text in task.title.lower()
                    or text in task.category.lower()
                    or text in task.description.lower()
                )
            ]

        tasks = [
            task
            for task in tasks
            if self._matches_filter(task)
        ]

        tasks = self._sort_tasks(tasks)

        today = datetime.now().strftime("%Y-%m-%d")

        today_tasks = [
            task
            for task in tasks
            if not task.completed
            and (
                not task.task_date
                or task.task_date == today
            )
        ]

        upcoming = [
            task
            for task in tasks
            if not task.completed
            and task.task_date
            and task.task_date > today
        ]

        completed = [
            task
            for task in tasks
            if task.completed
        ]

        if self.current_filter == "Today":
            groups = (("Today", today_tasks),)

        elif self.current_filter == "Upcoming":
            groups = (("Upcoming", upcoming),)

        elif self.current_filter == "Completed":
            groups = (("Completed", completed),)

        else:
            groups = (
                ("Today", today_tasks),
                ("Upcoming", upcoming),
                ("Completed", completed),
            )

        for title, group_tasks in groups:

            if not group_tasks:
                continue

            self._add_group(title, group_tasks)

        if not any(group for _name, group in groups):

            empty = QLabel("Nothing here yet.")
            empty.setObjectName("emptyTasks")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.taskLayout.insertWidget(0, empty)

        self._refresh_summary()

        if self.selected_task is not None:
            current = next(
                (
                    task
                    for task in self.task_manager.get_all_tasks()
                    if task.id == self.selected_task.id
                ),
                None
            )
            self.selected_task = current

        self._render_details()


    def _add_group(self, title, tasks):

        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        head = QHBoxLayout()

        name = QLabel(title)
        name.setObjectName("taskGroupTitle")

        count = QLabel(
            f"{len(tasks)} task"
            if len(tasks) == 1
            else f"{len(tasks)} tasks"
        )
        count.setObjectName("taskGroupCount")

        head.addWidget(name)
        head.addWidget(count)
        head.addStretch(1)

        layout.addLayout(head)

        for task in tasks:
            layout.addWidget(
                self._task_row(task)
            )

        self.taskLayout.insertWidget(
            self.taskLayout.count() - 1,
            wrap
        )


    def _task_row(self, task):

        row = QFrame()
        row.setObjectName("taskRow")
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.mousePressEvent = (
            lambda event, t=task:
                self.select_task(t)
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        checkbox = QPushButton(
            "✓" if task.completed else ""
        )
        checkbox.setObjectName(
            "taskCheckDone"
            if task.completed
            else "taskCheck"
        )
        checkbox.setFixedSize(24, 24)
        checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        checkbox.clicked.connect(
            lambda _checked=False, t=task:
                self.toggle_task(t)
        )

        title = QLabel(task.title)
        title.setObjectName(
            "taskRowTitleDone"
            if task.completed
            else "taskRowTitle"
        )

        category = QLabel(task.category)
        category.setObjectName("taskCategory")

        due_text = "Today"

        if task.task_date:
            due_text = task.task_date

        due = QLabel(due_text)
        due.setObjectName("taskDue")

        priority = QLabel(
            "Medium"
            if task.priority == "Normal"
            else task.priority
        )
        priority.setObjectName(
            "priorityHigh"
            if task.priority == "High"
            else (
                "priorityLow"
                if task.priority == "Low"
                else "priorityNormal"
            )
        )

        more = QPushButton("•••")
        more.setObjectName("taskMore")
        more.setFixedWidth(34)
        more.clicked.connect(
            lambda _checked=False, t=task:
                self.edit_task(t)
        )

        layout.addWidget(checkbox)
        layout.addWidget(title, 1)
        layout.addWidget(category)
        layout.addWidget(due)
        layout.addWidget(priority)
        layout.addWidget(more)

        return row


    def select_task(self, task):

        self.selected_task = task
        self._render_details()


    def toggle_task(self, task):

        self.task_manager.complete_task(
            task.id,
            not task.completed
        )

        self.load_tasks()


    def edit_task(self, task):

        dialog = EditTaskDialog(task)
        dialog.taskUpdated.connect(self._save_edit)

        if dialog.exec():
            self.load_tasks()


    def _save_edit(
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
        important,
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
            important=important,
        )


    def quick_add(self):

        title = self.quickTitle.text().strip()

        if not title:
            self.quickTitle.setFocus()
            return

        self.task_manager.create_task(
            title=title,
            task_date=self.quickDate.date().toString("yyyy-MM-dd"),
            priority=self.quickPriority.currentText(),
            category=self.quickCategory.currentText(),
            color=ThemeManager.get().Colors.PRIMARY,
        )

        self.quickTitle.clear()
        self.quickDate.setDate(QDate.currentDate())
        self.quickPriority.setCurrentText("Normal")

        self.load_tasks()


    def _refresh_summary(self):

        tasks = self.task_manager.get_all_tasks()
        today = datetime.now().strftime("%Y-%m-%d")

        completed_today = sum(
            1
            for task in tasks
            if (
                task.completed
                and task.completed_at
                and task.completed_at.startswith(today)
            )
        )

        upcoming = sum(
            1
            for task in tasks
            if (
                not task.completed
                and task.task_date
                and task.task_date > today
            )
        )

        focus = self.focus_manager.get_week_minutes()

        self.completedSummary["value"].setText(
            str(completed_today)
        )
        self.upcomingSummary["value"].setText(
            str(upcoming)
        )

        if focus >= 60:
            hours, minutes = divmod(focus, 60)
            text = (
                f"{hours}h {minutes}m"
                if minutes
                else f"{hours}h"
            )
        else:
            text = f"{focus}m"

        self.focusSummary["value"].setText(text)


    def _render_details(self):

        while self.detailBody.count():

            item = self.detailBody.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        if self.selected_task is None:

            icon = QLabel("▤")
            icon.setObjectName("detailEmptyIcon")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text = QLabel(
                "Select a task to view details\n"
                "Add notes, set reminders, and track it here."
            )
            text.setObjectName("detailEmptyText")
            text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text.setWordWrap(True)

            self.detailBody.addStretch(1)
            self.detailBody.addWidget(icon)
            self.detailBody.addWidget(text)
            self.detailBody.addStretch(1)

            return

        task = self.selected_task

        title = QLabel(task.title)
        title.setObjectName("detailTaskTitle")
        title.setWordWrap(True)

        meta = QLabel(
            f"{task.category}  •  {task.priority}  •  "
            f"{task.task_date or 'No due date'}"
        )
        meta.setObjectName("detailMeta")
        meta.setWordWrap(True)

        description = QLabel(
            task.description or "No description yet."
        )
        description.setObjectName("detailDescription")
        description.setWordWrap(True)

        edit = QPushButton("Edit Task")
        edit.setObjectName("detailEdit")
        edit.setCursor(Qt.CursorShape.PointingHandCursor)
        edit.clicked.connect(
            lambda _checked=False, t=task:
                self.edit_task(t)
        )

        self.detailBody.addWidget(title)
        self.detailBody.addWidget(meta)
        self.detailBody.addWidget(description)
        self.detailBody.addStretch(1)
        self.detailBody.addWidget(edit)


    def apply_theme(self):

        theme = ThemeManager.get()
        c = theme.Colors

        self.setStyleSheet(
            f"""
            QWidget {{
                background:transparent;
            }}

            QLabel#tasksEyebrow {{
                color:{c.TEXT};
                font-size:23px;
                font-weight:700;
                background:transparent;
            }}

            QLabel#tasksHero {{
                color:{c.PRIMARY};
                font-size:34px;
                font-weight:900;
                background:transparent;
            }}

            QLabel#tasksDate,
            QLabel#toolbarLabel,
            QLabel#taskGroupCount,
            QLabel#taskDue,
            QLabel#summaryCaption,
            QLabel#detailMeta,
            QLabel#detailDescription,
            QLabel#detailEmptyText {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                font-size:11px;
            }}

            QLineEdit#tasksSearch,
            QLineEdit#quickTitle,
            QComboBox#tasksSort,
            QComboBox#quickInput,
            QDateEdit#quickInput {{
                background:{c.SURFACE};
                color:{c.TEXT};
                border:1px solid {c.BORDER};
                border-radius:13px;
                padding:8px 11px;
            }}

            QLineEdit#tasksSearch:focus,
            QLineEdit#quickTitle:focus,
            QComboBox#tasksSort:focus,
            QDateEdit#quickInput:focus {{
                border-color:{c.BORDER_ACTIVE};
            }}

            QFrame#tasksToolbar {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:14px;
            }}

            QPushButton#taskTab {{
                background:transparent;
                color:{c.TEXT_SECONDARY};
                border:none;
                border-radius:10px;
                padding:8px 22px;
                font-size:11px;
            }}

            QPushButton#taskTab[active="true"] {{
                background:{c.PRIMARY};
                color:white;
                font-weight:750;
            }}

            QLabel#taskGroupTitle {{
                color:{c.TEXT};
                background:transparent;
                font-size:18px;
                font-weight:800;
            }}

            QFrame#taskRow {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:12px;
            }}

            QFrame#taskRow:hover {{
                border-color:{c.BORDER_ACTIVE};
                background:{c.SURFACE_ALT};
            }}

            QPushButton#taskCheck,
            QPushButton#taskCheckDone {{
                background:transparent;
                color:white;
                border:2px solid {c.TEXT_SECONDARY};
                border-radius:12px;
                font-weight:800;
            }}

            QPushButton#taskCheckDone {{
                background:{c.PRIMARY};
                border-color:{c.PRIMARY};
            }}

            QLabel#taskRowTitle {{
                color:{c.TEXT};
                background:transparent;
                font-size:12px;
                font-weight:600;
            }}

            QLabel#taskRowTitleDone {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                font-size:12px;
                text-decoration:line-through;
            }}

            QLabel#taskCategory {{
                color:{c.PRIMARY};
                background:rgba(70,115,255,0.14);
                border:1px solid rgba(70,115,255,0.18);
                border-radius:9px;
                padding:4px 9px;
                font-size:10px;
            }}

            QLabel#priorityHigh {{
                color:#FF818A;
                background:rgba(255,90,100,0.12);
                border:1px solid rgba(255,90,100,0.20);
                border-radius:10px;
                padding:4px 9px;
                font-size:10px;
            }}

            QLabel#priorityNormal {{
                color:#FFD06A;
                background:rgba(255,190,80,0.10);
                border:1px solid rgba(255,190,80,0.18);
                border-radius:10px;
                padding:4px 9px;
                font-size:10px;
            }}

            QLabel#priorityLow {{
                color:{c.PRIMARY};
                background:rgba(70,115,255,0.10);
                border:1px solid rgba(70,115,255,0.18);
                border-radius:10px;
                padding:4px 9px;
                font-size:10px;
            }}

            QPushButton#taskMore {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                border:none;
                font-size:14px;
            }}

            QFrame#taskSideCard {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:14px;
            }}

            QLabel#sideTitle {{
                color:{c.TEXT};
                background:transparent;
                font-size:16px;
                font-weight:800;
            }}

            QFrame#summaryRow {{
                background:{c.SURFACE_ALT};
                border:1px solid {c.BORDER};
                border-radius:11px;
            }}

            QLabel#summaryIcon {{
                color:{c.PRIMARY};
                background:rgba(70,115,255,0.14);
                border:1px solid rgba(70,115,255,0.18);
                border-radius:21px;
                font-size:17px;
                font-weight:800;
            }}

            QLabel#summaryValue {{
                color:{c.TEXT};
                background:transparent;
                font-size:20px;
                font-weight:800;
            }}

            QPushButton#quickAddButton,
            QPushButton#detailEdit {{
                background:{c.PRIMARY};
                color:white;
                border:none;
                border-radius:12px;
                padding:10px 14px;
                font-weight:800;
            }}

            QLabel#detailEmptyIcon {{
                color:{c.TEXT_SECONDARY};
                background:transparent;
                font-size:34px;
            }}

            QLabel#detailTaskTitle {{
                color:{c.TEXT};
                background:transparent;
                font-size:18px;
                font-weight:800;
            }}

            QLabel#emptyTasks {{
                color:{c.TEXT_SECONDARY};
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:14px;
                padding:40px;
                font-size:12px;
            }}
            """
        )


    def refresh_theme(self):

        self.apply_theme()
        self.load_tasks()


    def showEvent(self, event):

        super().showEvent(event)
        self.load_tasks()
