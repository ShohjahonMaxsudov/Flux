from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFrame
)

from PySide6.QtCore import QTimer

from ui.taskcard import TaskCard
from ui.add_task_dialog import AddTaskDialog
from ui.edit_task_dialog import EditTaskDialog
from ui.toast import notify
from utils.task_manager import TaskManager
from utils.glass_effects import GlassFrame
from themes.manager import ThemeManager


class TasksPage(QWidget):

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
            16
        )



        # HEADER

        self.title = QLabel(
            "Tasks"
        )


        self.subtitle = QLabel(
            "Manage everything in one place."
        )


        root.addWidget(
            self.title
        )


        root.addWidget(
            self.subtitle
        )



        # TOOLBAR

        tools = QHBoxLayout()


        self.search = QLineEdit()


        self.search.setPlaceholderText(
            "Search tasks..."
        )



        self.filter = QComboBox()


        self.filter.addItems(
            [
                "All",
                "Completed",
                "Pending",
                "Important",
                "High Priority"
            ]
        )



        self.sort = QComboBox()


        self.sort.addItems(
            [
                "Priority",
                "Newest",
                "Oldest",
                "Due Date",
                "Title A-Z"
            ]
        )


        self.addButton = QPushButton(
            "+ Add Task"
        )


        self.addButton.clicked.connect(
            self.open_add_task
        )


        self.refreshButton = QPushButton(
            "Refresh"
        )


        self.refreshButton.clicked.connect(
            self.load_tasks
        )



        tools.addWidget(
            self.search
        )


        tools.addWidget(
            self.filter
        )


        tools.addWidget(
            self.sort
        )


        tools.addWidget(
            self.addButton
        )


        tools.addWidget(
            self.refreshButton
        )


        root.addLayout(
            tools
        )



        # TASK AREA

        self.container = GlassFrame()

        self.container.setObjectName(
            "tasksListCard"
        )


        self.taskLayout = QVBoxLayout(
            self.container
        )


        self.taskLayout.setContentsMargins(
            20,
            20,
            20,
            20
        )


        self.taskLayout.setSpacing(
            10
        )


        root.addWidget(
            self.container
        )



        self.search.textChanged.connect(
            self.load_tasks
        )


        self.filter.currentTextChanged.connect(
            self.load_tasks
        )


        self.sort.currentTextChanged.connect(
            self.load_tasks
        )


        self.apply_theme()

        self.load_tasks()



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


        self.search.setStyleSheet(
            f"""
            QLineEdit{{

                background:{theme.Colors.SURFACE_ALT};

                color:{theme.Colors.TEXT};

                border:1px solid {theme.Colors.BORDER};

                border-radius:12px;

                padding:10px;

            }}

            QLineEdit:focus{{

                border:1px solid {theme.Colors.PRIMARY};

            }}
            """
        )


        self.filter.setStyleSheet(
            f"""
            QComboBox{{

                background:{theme.Colors.SURFACE_ALT};

                color:{theme.Colors.TEXT};

                border:1px solid {theme.Colors.BORDER};

                border-radius:12px;

                padding:10px;

            }}

            QComboBox QAbstractItemView{{

                background:{theme.Colors.SURFACE};

                color:{theme.Colors.TEXT};

                selection-background-color:{theme.Colors.PRIMARY};

            }}
            """
        )


        self.sort.setStyleSheet(
            self.filter.styleSheet()
        )


        self.addButton.setStyleSheet(
            f"""
            QPushButton{{

                background:{theme.Colors.GLASS};

                color:{theme.Colors.TEXT};

                border:1px solid {theme.Colors.BORDER};

                border-radius:12px;

                padding:10px 18px;

                font-weight:bold;

            }}

            QPushButton:hover{{

                background:{theme.Colors.GLASS_HOVER};

                border:1px solid {theme.Colors.PRIMARY};

            }}
            """
        )


        self.refreshButton.setStyleSheet(
            f"""
            QPushButton{{

                background:{theme.Colors.PRIMARY};

                color:white;

                border-radius:12px;

                padding:10px 20px;

                font-weight:bold;

            }}

            QPushButton:hover{{

                background:{theme.Colors.BORDER_ACTIVE};

            }}
            """
        )


        self.container.setStyleSheet(
            f"""
            QFrame#tasksListCard{{

                background:{theme.Colors.GLASS};

                border-radius:20px;

                border:1px solid {theme.Colors.BORDER};

            }}
            """
        )



    def refresh_theme(self):

        self.apply_theme()

        self.load_tasks()



    def showEvent(self, event):

        # Pages persist for the app's whole lifetime (PageManager just
        # hides/shows the same instances), so without this the Tasks
        # page would keep showing whatever it looked like the last time
        # its own search/filter/refresh triggered a reload — not
        # necessarily what's true now if a task was added or completed
        # from the Dashboard in between.

        super().showEvent(event)

        # Render the page first; refresh on the next event-loop turn so
        # switching tabs never waits on database/UI rebuild work.
        QTimer.singleShot(0, self.load_tasks)



    def load_tasks(self):


        while self.taskLayout.count():

            item = self.taskLayout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.hide()

                widget.deleteLater()



        tasks = self.task_manager.get_all_tasks()


        text = self.search.text().lower()


        if text:

            tasks = [

                task

                for task in tasks

                if text in task.title.lower()

            ]


        mode = self.filter.currentText()


        if mode == "Completed":
            tasks = [task for task in tasks if task.completed]

        elif mode == "Pending":
            tasks = [task for task in tasks if not task.completed]

        elif mode == "Important":
            tasks = [task for task in tasks if task.important]

        elif mode == "High Priority":
            tasks = [task for task in tasks if task.priority == "High"]


        sort_mode = self.sort.currentText()

        if sort_mode == "Newest":

            tasks = sorted(tasks, key=lambda t: t.id, reverse=True)

        elif sort_mode == "Oldest":

            tasks = sorted(tasks, key=lambda t: t.id)

        elif sort_mode == "Due Date":

            tasks = sorted(
                tasks,
                key=lambda t: (t.task_date or "9999-99-99", t.time or "99:99")
            )

        elif sort_mode == "Title A-Z":

            tasks = sorted(tasks, key=lambda t: t.title.lower())

        # else "Priority" - the order get_all_tasks() already returned
        # (completed last, high priority first), unchanged.


        theme = ThemeManager.get()


        if not tasks:

            empty = QLabel(
                "No tasks found"
            )


            empty.setStyleSheet(
                f"""
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:16px;
                background:transparent;
                border:none;
                """
            )


            self.taskLayout.addWidget(
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

                    important=task.important,

                    task_date=task.task_date

                )


                card.checkedChanged.connect(

                    lambda checked, t=task:

                    self.on_task_completed(
                        t.id,
                        checked
                    )

                )


                card.deleteClicked.connect(

                    lambda t=task:

                    self.on_delete_task(
                        t
                    )

                )


                card.editClicked.connect(

                    lambda t=task:

                    self.open_edit_task(
                        t
                    )

                )


                self.taskLayout.addWidget(
                    card
                )


        self.taskLayout.addStretch()



    def on_task_completed(
        self,
        task_id,
        checked
    ):

        self.task_manager.complete_task(
            task_id,
            checked
        )

        self.load_tasks()



    def on_delete_task(
        self,
        task
    ):

        snapshot = dict(
            title=task.title,
            time=task.time,
            task_date=task.task_date,
            priority=task.priority,
            category=task.category,
            description=task.description,
            color=task.color,
            reminder=task.reminder,
            repeat=task.repeat,
            important=task.important
        )

        was_completed = task.completed

        title = task.title

        self.task_manager.remove_task(
            task.id
        )

        self.load_tasks()

        notify(
            f'Deleted "{title}"' if title else "Task deleted",
            "info",
            action=("Undo", lambda: self._undo_delete(snapshot, was_completed))
        )


    def _undo_delete(self, snapshot, was_completed):

        new_id = self.task_manager.create_task(**snapshot)

        if was_completed and new_id:

            self.task_manager.complete_task(new_id, True)

        self.load_tasks()

        notify("Task restored", "success")


    def open_add_task(self):

        dialog = AddTaskDialog()

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
        task_date,
        description,
        color,
        reminder,
        repeat,
        important
    ):

        self.task_manager.create_task(
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

        self.load_tasks()

        notify(
            f'Added "{title}"' if title else "Task added",
            "success"
        )



    def open_edit_task(
        self,
        task
    ):

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

        self.load_tasks()

        notify(
            f'Updated "{title}"' if title else "Task updated",
            "success"
        )
