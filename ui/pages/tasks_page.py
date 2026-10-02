from datetime import datetime, timedelta

from PySide6.QtCore import QDate, Qt, Signal
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
from ui.design_system import AccentOrb, CheckButton, ClickableFrame, GradientButton, HeaderPill, IconCircle, Metrics, SurfaceCard, clear_layout
from ui.edit_task_dialog import EditTaskDialog
from ui.icons import IconGlyph
from utils.focus_manager import FocusManager
from utils.task_manager import TaskManager


CATEGORY_COLORS = {
    "Work": ("#74A7FF", "rgba(60,105,205,0.18)"),
    "Study": ("#AF8BFF", "rgba(125,80,220,0.18)"),
    "Planning": ("#91A7D9", "rgba(90,115,165,0.18)"),
    "Fitness": ("#5BD69A", "rgba(60,175,120,0.17)"),
    "Health": ("#5BD69A", "rgba(60,175,120,0.17)"),
    "Coding": ("#70D6FF", "rgba(70,155,195,0.17)"),
    "Personal": ("#C19BFF", "rgba(130,85,205,0.18)"),
    "General": ("#9CB0CF", "rgba(100,120,155,0.16)"),
}


class TaskRow(ClickableFrame):
    toggleRequested = Signal(object)
    editRequested = Signal(object)

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("taskRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 10, 10)
        layout.setSpacing(10)

        self.check = CheckButton(task.completed, size=24)
        self.check.clicked.connect(lambda: self.toggleRequested.emit(task))

        self.title = QLabel(task.title)
        self.title.setObjectName("taskTitleDone" if task.completed else "taskTitle")
        self.title.setMinimumWidth(150)

        category = QLabel(task.category or "General")
        category.setObjectName("categoryChip")
        fg, bg = CATEGORY_COLORS.get(task.category or "General", CATEGORY_COLORS["General"])
        category.setStyleSheet(
            f"color:{fg}; background:{bg}; border:1px solid {fg}33; border-radius:9px; padding:4px 9px; font-size:10px;"
        )

        due = QLabel(self._friendly_date(task.task_date, task.completed))
        due.setObjectName("taskDue")
        due.setMinimumWidth(72)
        due.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        priority = QLabel("Medium" if task.priority == "Normal" else task.priority)
        priority.setObjectName(
            "priorityHigh" if task.priority == "High" else ("priorityLow" if task.priority == "Low" else "priorityMedium")
        )
        priority.setMinimumWidth(58)
        priority.setAlignment(Qt.AlignmentFlag.AlignCenter)

        more = QPushButton()
        more.setObjectName("taskMore")
        more.setFixedSize(30, 30)
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        more.clicked.connect(lambda: self.editRequested.emit(task))
        more_layout = QHBoxLayout(more)
        more_layout.setContentsMargins(6, 6, 6, 6)
        self.more_icon = IconGlyph("more", size=16)
        self.more_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        more_layout.addWidget(self.more_icon)

        layout.addWidget(self.check)
        layout.addWidget(self.title, 1)
        layout.addWidget(category)
        layout.addWidget(due)
        layout.addWidget(priority)
        layout.addWidget(more)

        self.apply_theme()

    @staticmethod
    def _friendly_date(value, completed=False):
        if completed:
            return "Today" if value == datetime.now().strftime("%Y-%m-%d") else (value or "")
        if not value:
            return "Today"
        try:
            day = datetime.strptime(value, "%Y-%m-%d").date()
            today = datetime.now().date()
            delta = (day - today).days
            if delta < 0:
                return "Overdue"
            if delta == 0:
                return "Today"
            if delta == 1:
                return "Tomorrow"
            if delta < 7:
                return day.strftime("%a")
            return day.strftime("%b %d")
        except (TypeError, ValueError):
            return value

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.more_icon.setColor(c.TEXT_SECONDARY)
        self.setStyleSheet(
            f"""
            QFrame#taskRow {{
                background:{c.SURFACE};
                border:1px solid {c.BORDER};
                border-radius:11px;
            }}
            QFrame#taskRow:hover {{
                background:{c.SURFACE_ALT};
                border-color:rgba(115,150,220,0.30);
            }}
            QLabel#taskTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:11px; font-weight:600; }}
            QLabel#taskTitleDone {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:11px; text-decoration:line-through; }}
            QLabel#taskDue {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px; }}
            QLabel#priorityHigh {{ color:#FF8492; background:rgba(220,70,85,0.13); border:1px solid rgba(255,100,120,0.20); border-radius:10px; padding:4px 8px; font-size:10px; }}
            QLabel#priorityMedium {{ color:#F2CB69; background:rgba(205,155,55,0.12); border:1px solid rgba(240,195,80,0.18); border-radius:10px; padding:4px 8px; font-size:10px; }}
            QLabel#priorityLow {{ color:#7DAAFF; background:rgba(70,105,210,0.12); border:1px solid rgba(90,135,245,0.20); border-radius:10px; padding:4px 8px; font-size:10px; }}
            QPushButton#taskMore {{ background:transparent; border:none; border-radius:8px; }}
            QPushButton#taskMore:hover {{ background:rgba(100,125,165,0.12); }}
            """
        )


class TasksPage(QWidget):
    def __init__(self):
        super().__init__()

        self.task_manager = TaskManager()
        self.focus_manager = FocusManager()
        self.selected_task = None
        self.current_filter = "All"

        root = QVBoxLayout(self)
        root.setContentsMargins(Metrics.PAGE_X, Metrics.PAGE_Y, Metrics.PAGE_X, Metrics.PAGE_Y)
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
        right.setSpacing(10)
        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        self.search = QLineEdit()
        self.search.setObjectName("tasksSearch")
        self.search.setPlaceholderText("Search tasks…")
        self.search.setFixedWidth(305)
        self.search.textChanged.connect(self.load_tasks)
        self.avatar = AccentOrb(38)
        search_row.addWidget(self.search)
        search_row.addWidget(self.avatar)
        self.date_label = QLabel()
        self.date_label.setObjectName("tasksDate")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addLayout(search_row)
        right.addWidget(self.date_label)

        header.addLayout(heading, 1)
        header.addLayout(right)
        root.addLayout(header)

        toolbar = QFrame()
        toolbar.setObjectName("tasksToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(7, 7, 7, 7)
        toolbar_layout.setSpacing(4)

        self.tabs = {}
        for key in ("All", "Today", "Upcoming", "Completed"):
            button = QPushButton(key)
            button.setObjectName("taskTab")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, k=key: self.set_filter(k))
            self.tabs[key] = button
            toolbar_layout.addWidget(button)

        toolbar_layout.addStretch(1)

        sort_icon = IconGlyph("sort", size=15)
        sort_icon.setColor(ThemeManager.get().Colors.TEXT_SECONDARY)
        toolbar_layout.addWidget(sort_icon)

        self.sort = QComboBox()
        self.sort.setObjectName("tasksSort")
        self.sort.addItems(("Priority", "Due Date", "Newest", "Title A-Z"))
        self.sort.currentTextChanged.connect(self.load_tasks)
        toolbar_layout.addWidget(self.sort)

        self.filter_button = QPushButton()
        self.filter_button.setObjectName("filterButton")
        self.filter_button.setFixedSize(38, 34)
        self.filter_button.setCursor(Qt.CursorShape.PointingHandCursor)
        filter_layout = QHBoxLayout(self.filter_button)
        filter_layout.setContentsMargins(9, 7, 9, 7)
        self.filter_icon = IconGlyph("filter", size=18)
        self.filter_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        filter_layout.addWidget(self.filter_icon)
        self.filter_button.clicked.connect(self._cycle_filter)
        toolbar_layout.addWidget(self.filter_button)

        root.addWidget(toolbar)

        body = QHBoxLayout()
        body.setSpacing(14)

        self.task_scroll = QScrollArea()
        self.task_scroll.setWidgetResizable(True)
        self.task_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.task_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.task_scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} QScrollArea>QWidget>QWidget{background:transparent;}")

        self.task_host = QWidget()
        self.task_host.setStyleSheet("background:transparent;")
        self.task_layout = QVBoxLayout(self.task_host)
        self.task_layout.setContentsMargins(0, 0, 4, 0)
        self.task_layout.setSpacing(14)
        self.task_layout.addStretch(1)
        self.task_scroll.setWidget(self.task_host)
        body.addWidget(self.task_scroll, 1)

        self.side = QWidget()
        self.side.setFixedWidth(330)
        side_layout = QVBoxLayout(self.side)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(12)

        self.summary_card = SurfaceCard("Productivity Summary")
        self.summary_card.setMinimumHeight(242)
        self.summary_period = HeaderPill("This Week")
        self.summary_card.set_header_action(self.summary_period)
        self.completed_summary = self._summary_row("Completed Today", "check", "Today")
        self.upcoming_summary = self._summary_row("Upcoming Tasks", "calendar", "Next")
        self.focus_summary = self._summary_row("Focus Time", "chart", "This week")
        for item in (self.completed_summary, self.upcoming_summary, self.focus_summary):
            self.summary_card.body.addWidget(item["frame"])
        side_layout.addWidget(self.summary_card)

        self.quick_card = SurfaceCard("Quick Add Task")
        self.quick_card.setMinimumHeight(182)
        self.quick_title = QLineEdit()
        self.quick_title.setObjectName("quickTitle")
        self.quick_title.setPlaceholderText("What do you want to get done?")
        self.quick_title.returnPressed.connect(self.quick_add)
        self.quick_card.body.addWidget(self.quick_title)

        meta = QHBoxLayout()
        meta.setSpacing(7)
        self.quick_date = QDateEdit(QDate.currentDate())
        self.quick_date.setObjectName("quickInput")
        self.quick_date.setCalendarPopup(True)
        self.quick_date.setDisplayFormat("dd MMM")
        self.quick_priority = QComboBox()
        self.quick_priority.setObjectName("quickInput")
        self.quick_priority.addItems(("Low", "Normal", "High"))
        self.quick_priority.setCurrentText("Normal")
        self.quick_category = QComboBox()
        self.quick_category.setObjectName("quickInput")
        self.quick_category.addItems(("General", "Study", "Work", "Fitness", "Health", "Coding", "Personal"))
        meta.addWidget(self.quick_date)
        meta.addWidget(self.quick_priority)
        meta.addWidget(self.quick_category)
        self.quick_card.body.addLayout(meta)

        self.quick_button = GradientButton("Add Task", "plus")
        self.quick_button.clicked.connect(self.quick_add)
        self.quick_card.body.addWidget(self.quick_button)
        side_layout.addWidget(self.quick_card)

        self.detail_card = SurfaceCard("Task Details")
        self.detail_card.setMinimumHeight(190)
        self.detail_body = QVBoxLayout()
        self.detail_body.setSpacing(9)
        self.detail_card.body.addLayout(self.detail_body)
        side_layout.addWidget(self.detail_card, 1)

        body.addWidget(self.side)
        root.addLayout(body, 1)

        self.apply_theme()
        self.set_filter("All")
        self.load_tasks()

    def _summary_row(self, label, icon_name, micro):
        frame = QFrame()
        frame.setObjectName("summaryRow")
        frame.setFixedHeight(58)
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)

        icon = IconCircle(icon_name, 42)
        text = QVBoxLayout()
        text.setSpacing(0)
        value = QLabel("0")
        value.setObjectName("summaryValue")
        caption = QLabel(label)
        caption.setObjectName("summaryCaption")
        text.addWidget(value)
        text.addWidget(caption)
        micro_label = QLabel(micro)
        micro_label.setObjectName("summaryMicro")

        row.addWidget(icon)
        row.addLayout(text, 1)
        row.addWidget(micro_label)
        return {"frame": frame, "value": value, "icon": icon}

    def _cycle_filter(self):
        order = ("All", "Today", "Upcoming", "Completed")
        try:
            index = order.index(self.current_filter)
        except ValueError:
            index = 0
        self.set_filter(order[(index + 1) % len(order)])


    def set_filter(self, key):
        self.current_filter = key
        for tab_key, button in self.tabs.items():
            button.setProperty("active", tab_key == key)
            button.style().unpolish(button)
            button.style().polish(button)
        self.load_tasks()

    def _matches_filter(self, task):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.current_filter == "Completed":
            return task.completed
        if self.current_filter == "Today":
            return not task.completed and (not task.task_date or task.task_date <= today)
        if self.current_filter == "Upcoming":
            return not task.completed and bool(task.task_date and task.task_date > today)
        return True

    def _sort_tasks(self, tasks):
        mode = self.sort.currentText()
        if mode == "Priority":
            return sorted(tasks, key=lambda t: (t.completed, t.priority_order, t.task_date or "9999-99-99"))
        if mode == "Due Date":
            return sorted(tasks, key=lambda t: (t.completed, t.task_date or "9999-99-99"))
        if mode == "Title A-Z":
            return sorted(tasks, key=lambda t: t.title.lower())
        return sorted(tasks, key=lambda t: t.id, reverse=True)

    def load_tasks(self):
        self._sync_header()
        clear_layout(self.task_layout, keep_stretch=True)

        tasks = self.task_manager.get_all_tasks()
        query = self.search.text().strip().lower()
        if query:
            tasks = [
                t for t in tasks
                if query in t.title.lower() or query in t.category.lower() or query in (t.description or "").lower()
            ]
        tasks = [t for t in tasks if self._matches_filter(t)]
        tasks = self._sort_tasks(tasks)

        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = [t for t in tasks if not t.completed and (not t.task_date or t.task_date <= today)]
        upcoming = [t for t in tasks if not t.completed and t.task_date and t.task_date > today]
        completed = [t for t in tasks if t.completed]

        if self.current_filter == "Today":
            groups = (("Today", today_tasks),)
        elif self.current_filter == "Upcoming":
            groups = (("Upcoming", upcoming),)
        elif self.current_filter == "Completed":
            groups = (("Completed", completed),)
        else:
            groups = (("Today", today_tasks), ("Upcoming", upcoming), ("Completed", completed))

        added = False
        for title, group in groups:
            if group:
                self._add_group(title, group)
                added = True

        if not added:
            empty = QLabel("Nothing here yet.")
            empty.setObjectName("emptyTasks")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_layout.insertWidget(0, empty)

        self._refresh_summary()
        self._refresh_selected()
        self._render_details()

    def _sync_header(self):
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
        self.eyebrow.setText(greeting)
        self.date_label.setText(datetime.now().strftime("%a, %b %d, %Y"))

    def _add_group(self, title, tasks):
        group_widget = QWidget()
        group_widget.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(group_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        head = QHBoxLayout()
        chevron = IconGlyph("chevron_down", size=16)
        chevron.setColor(ThemeManager.get().Colors.BLUE_SOFT)
        name = QLabel(title)
        name.setObjectName("groupTitle")
        count = QLabel(f"{len(tasks)} task" if len(tasks) == 1 else f"{len(tasks)} tasks")
        count.setObjectName("groupCount")
        head.addWidget(chevron)
        head.addWidget(name)
        head.addWidget(count)
        head.addStretch(1)
        layout.addLayout(head)

        group_widget.setMinimumHeight(
            28 + len(tasks) * 58
        )

        for task in tasks:
            row = TaskRow(task)
            row.clicked.connect(lambda t=task: self.select_task(t))
            row.toggleRequested.connect(self.toggle_task)
            row.editRequested.connect(self.edit_task)
            layout.addWidget(row)

        self.task_layout.insertWidget(self.task_layout.count() - 1, group_widget)

    def select_task(self, task):
        self.selected_task = task
        self._render_details()

    def toggle_task(self, task):
        self.task_manager.complete_task(task.id, not task.completed)
        self.load_tasks()

    def edit_task(self, task):
        dialog = EditTaskDialog(task)
        dialog.taskUpdated.connect(self._save_edit)
        dialog.exec()
        self.load_tasks()

    def _save_edit(self, task_id, title, time, priority, category, task_date, description, color, reminder, repeat, important):
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
        title = self.quick_title.text().strip()
        if not title:
            self.quick_title.setFocus()
            return

        self.task_manager.create_task(
            title=title,
            task_date=self.quick_date.date().toString("yyyy-MM-dd"),
            priority=self.quick_priority.currentText(),
            category=self.quick_category.currentText(),
            color=ThemeManager.get().Colors.PRIMARY,
        )
        self.quick_title.clear()
        self.quick_date.setDate(QDate.currentDate())
        self.quick_priority.setCurrentText("Normal")
        self.load_tasks()

    def _refresh_summary(self):
        tasks = self.task_manager.get_all_tasks()
        today = datetime.now().strftime("%Y-%m-%d")
        next_week = (datetime.now().date() + timedelta(days=7)).strftime("%Y-%m-%d")

        completed_today = sum(
            1 for t in tasks
            if t.completed and t.completed_at and t.completed_at.startswith(today)
        )
        upcoming = sum(
            1 for t in tasks
            if not t.completed and t.task_date and today < t.task_date <= next_week
        )
        focus = self.focus_manager.get_week_minutes()

        self.completed_summary["value"].setText(str(completed_today))
        self.upcoming_summary["value"].setText(str(upcoming))
        self.focus_summary["value"].setText(self._focus_text(focus))

    @staticmethod
    def _focus_text(minutes):
        hours, mins = divmod(max(0, int(minutes or 0)), 60)
        return f"{hours}h {mins}m" if hours and mins else (f"{hours}h" if hours else f"{mins}m")

    def _refresh_selected(self):
        if self.selected_task is None:
            return
        self.selected_task = next(
            (t for t in self.task_manager.get_all_tasks() if t.id == self.selected_task.id),
            None,
        )

    def _render_details(self):
        clear_layout(self.detail_body)

        if self.selected_task is None:
            icon = IconCircle("notebook", 52)
            hint = QLabel("Select a task to view details")
            hint.setObjectName("detailHintTitle")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub = QLabel("See notes, due date, priority and edit the task here.")
            sub.setObjectName("detailHint")
            sub.setWordWrap(True)
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.detail_body.addStretch(1)
            self.detail_body.addWidget(icon, 0, Qt.AlignmentFlag.AlignHCenter)
            self.detail_body.addWidget(hint)
            self.detail_body.addWidget(sub)
            self.detail_body.addStretch(1)
            return

        task = self.selected_task
        title = QLabel(task.title)
        title.setObjectName("detailTitle")
        title.setWordWrap(True)
        meta = QLabel(f"{task.category or 'General'}  •  {'Medium' if task.priority == 'Normal' else task.priority}  •  {TaskRow._friendly_date(task.task_date)}")
        meta.setObjectName("detailMeta")
        meta.setWordWrap(True)
        description = QLabel(task.description or "No description yet.")
        description.setObjectName("detailDescription")
        description.setWordWrap(True)

        edit = QPushButton("Edit Task")
        edit.setObjectName("detailEdit")
        edit.setCursor(Qt.CursorShape.PointingHandCursor)
        edit.clicked.connect(lambda: self.edit_task(task))

        self.detail_body.addWidget(title)
        self.detail_body.addWidget(meta)
        self.detail_body.addSpacing(4)
        self.detail_body.addWidget(description)
        self.detail_body.addStretch(1)
        self.detail_body.addWidget(edit)

    def apply_theme(self):
        c = ThemeManager.get().Colors
        for card in (self.summary_card, self.quick_card, self.detail_card):
            card.apply_theme()
        self.summary_period.apply_theme()
        self.filter_icon.setColor(c.TEXT_SECONDARY)
        for item in (self.completed_summary, self.upcoming_summary, self.focus_summary):
            item["icon"].apply_theme()
        self.quick_button.apply_theme()

        self.setStyleSheet(
            f"""
            QLabel#tasksEyebrow {{ color:{c.TEXT}; background:transparent; border:none; font-size:24px; font-weight:700; }}
            QLabel#tasksHero {{ color:{c.PRIMARY_LIGHT}; background:transparent; border:none; font-size:30px; font-weight:800; }}
            QLabel#tasksDate {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px; }}
            QLineEdit#tasksSearch, QLineEdit#quickTitle, QComboBox#tasksSort, QComboBox#quickInput, QDateEdit#quickInput {{
                color:{c.TEXT}; background:{c.SURFACE}; border:1px solid {c.BORDER}; border-radius:11px; padding:8px 11px; font-size:10px;
            }}
            QLineEdit#tasksSearch {{ border-radius:16px; padding:9px 14px; font-size:11px; }}
            QLineEdit#tasksSearch:focus, QLineEdit#quickTitle:focus, QComboBox#tasksSort:focus, QComboBox#quickInput:focus, QDateEdit#quickInput:focus {{ border-color:{c.BORDER_ACTIVE}; }}
            QFrame#tasksToolbar {{ background:{c.SURFACE}; border:1px solid {c.BORDER}; border-radius:13px; }}
            QPushButton#filterButton {{ background:{c.SURFACE_ALT}; border:1px solid {c.BORDER}; border-radius:9px; }}
            QPushButton#filterButton:hover {{ border-color:{c.BORDER_ACTIVE}; background:rgba(80,105,155,0.16); }}
            QPushButton#taskTab {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; border-radius:9px; padding:8px 22px; font-size:10px; }}
            QPushButton#taskTab:hover {{ color:{c.TEXT}; background:rgba(80,105,155,0.12); }}
            QPushButton#taskTab[active="true"] {{ color:white; background:{c.PRIMARY}; font-weight:700; }}
            QLabel#groupTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:17px; font-weight:800; }}
            QLabel#groupCount {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px; }}
            QFrame#summaryRow {{ background:{c.SURFACE_ALT}; border:1px solid {c.BORDER}; border-radius:11px; }}
            QLabel#summaryValue {{ color:{c.TEXT}; background:transparent; border:none; font-size:20px; font-weight:800; }}
            QLabel#summaryCaption {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:9px; }}
            QLabel#summaryMicro {{ color:{c.GREEN}; background:transparent; border:none; font-size:9px; }}
            QLabel#detailHintTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:12px; font-weight:700; }}
            QLabel#detailHint, QLabel#detailMeta, QLabel#detailDescription {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px; }}
            QLabel#detailTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:17px; font-weight:800; }}
            QPushButton#detailEdit {{ color:white; background:{c.PRIMARY}; border:none; border-radius:10px; padding:9px 12px; font-weight:700; }}
            QLabel#emptyTasks {{ color:{c.TEXT_SECONDARY}; background:{c.SURFACE}; border:1px solid {c.BORDER}; border-radius:14px; padding:42px; font-size:11px; }}
            """
        )

    def refresh_theme(self):
        self.apply_theme()
        self.load_tasks()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_tasks()
