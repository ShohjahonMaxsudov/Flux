from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy
)

from PySide6.QtCore import Qt, Signal, QTimer

from ui.header import Header
from ui.statcard import StatCard
from ui.taskcard import TaskCard
from ui.quote_banner import QuoteBanner
from ui.add_task_dialog import AddTaskDialog
from ui.edit_task_dialog import EditTaskDialog
from ui.weekly_progress import WeeklyProgressCard
from ui.toast import notify

from utils.task_manager import TaskManager
from utils.settings_manager import SettingsManager
from themes.manager import ThemeManager



class Dashboard(QWidget):

    progressChanged = Signal(int)

    def __init__(self):

        super().__init__()


        self.task_manager = TaskManager()

        self.current_filter = "All"



        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )



        root = QVBoxLayout(self)

        root.setSpacing(18)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )



        self.header = Header()

        self.settings_manager = SettingsManager()

        self.header.set_user_name(
            self.settings_manager.get_user_name()
        )


        self.header.addTaskClicked.connect(
            self.open_add_task
        )


        root.addWidget(
            self.header
        )



        stats = QHBoxLayout()

        stats.setSpacing(16)



        self.todayCard = StatCard(
            "Today",
            "0",
            subtitle="Tasks on deck",
            icon="check",
            accent_index=0
        )

        self.completedCard = StatCard(
            "Completed",
            "0",
            subtitle="Finished",
            icon="check",
            accent_index=1
        )

        self.pendingCard = StatCard(
            "Pending",
            "0",
            subtitle="Still moving",
            icon="clock",
            accent_index=2
        )

        self.streakCard = StatCard(
            "Streak",
            "0 Days",
            subtitle="Consistency",
            icon="flame",
            accent_index=3
        )



        stats.addWidget(self.todayCard)
        stats.addWidget(self.completedCard)
        stats.addWidget(self.pendingCard)
        stats.addWidget(self.streakCard)


        root.addLayout(stats)



        self.container = QFrame()

        self.container.setObjectName(
            "dashboardScheduleCard"
        )



        box = QVBoxLayout(
            self.container
        )


        box.setContentsMargins(
            20,
            20,
            20,
            20
        )



        self.title = QLabel(
            "Today's Flow"
        )


        box.addWidget(
            self.title
        )



        self.taskLayout = QVBoxLayout()

        self.taskLayout.setSpacing(
            10
        )

        self.taskLayout.setContentsMargins(
            0,
            0,
            6,
            0
        )

        # The task list scrolls inside its card. Without this the card
        # (and with it the whole window) grew with every task added, and
        # nothing could sit below the list.

        self.taskHost = QWidget()

        self.taskHost.setLayout(
            self.taskLayout
        )

        self.taskScroll = QScrollArea()

        self.taskScroll.setWidgetResizable(True)

        self.taskScroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.taskScroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.taskScroll.setWidget(
            self.taskHost
        )

        box.addWidget(
            self.taskScroll,
            1
        )

        # Schedule on the left, this week's completed-task chart and
        # goal ring on the right — the "Weekly Progress" panel from the
        # original concept board.

        middleRow = QHBoxLayout()

        middleRow.setSpacing(20)

        middleRow.addWidget(
            self.container,
            3
        )

        self.weeklyCard = WeeklyProgressCard()

        middleRow.addWidget(
            self.weeklyCard,
            2
        )

        root.addLayout(
            middleRow,
            1
        )

        # Daily quote over a small themed landscape.

        self.banner = QuoteBanner()

        root.addWidget(
            self.banner
        )



        self.apply_theme()


        self.load_tasks()



    def apply_theme(self):

        theme = ThemeManager.get()



        self.setStyleSheet(
            f"""
            QWidget{{

                background:transparent;

                color:{theme.Colors.TEXT};

            }}
            """
        )



        self.container.setStyleSheet(
            f"""
            QFrame#dashboardScheduleCard{{

                background:{theme.Colors.GLASS};

                border:1px solid {theme.Colors.BORDER};

                border-radius:20px;

            }}
            """
        )



        self.title.setStyleSheet(
            f"""
            QLabel{{

                color:{theme.Colors.TEXT};

                font-size:24px;

                font-weight:700;

                background:transparent;

                border:none;

            }}
            """
        )



    def refresh_theme(self):

        # Called when the theme changes out from under an already-open
        # Dashboard. apply_theme() only restyled this widget's own
        # container/title; the header and stat cards built their
        # stylesheet once at construction and were left stale. Rebuilding
        # the task list also picks up the new theme for every TaskCard.

        self.apply_theme()

        self.header.apply_theme()

        self.todayCard.apply_theme()

        self.completedCard.apply_theme()

        self.pendingCard.apply_theme()

        self.streakCard.apply_theme()

        self.banner.apply_theme()

        self.weeklyCard.apply_theme()

        self.load_tasks()



    def set_user_name(self, name):

        self.settings_manager.set_user_name(name)

        self.header.set_user_name(name)



    def showEvent(self, event):

        # Dashboard is constructed once and kept alive for the app's
        # lifetime (PageManager just hides/shows it), so without this,
        # navigating back to it after completing/editing a task from
        # the Tasks or Calendar page would keep showing stale numbers
        # until something on the Dashboard itself triggered a reload.

        super().showEvent(event)

        self.load_tasks()



    # -------------------------
    # FILTER
    # -------------------------

    def set_filter(
        self,
        filter_name
    ):

        self.current_filter = filter_name

        self.load_tasks()



    # -------------------------
    # ADD
    # -------------------------

    def open_add_task(self):

        dialog = AddTaskDialog()


        dialog.taskCreated.connect(
            self.create_task
        )


        dialog.exec()



    def create_task(
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

        # Matches AddTaskDialog.taskCreated's emit order exactly:
        # title, time, priority, category, date, description, color,
        # reminder, repeat, important. Previously this method only
        # accepted the first four, so Qt silently dropped the other six
        # emitted values at the signal/slot boundary and they never even
        # reached TaskManager.

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



    # -------------------------
    # EDIT
    # -------------------------

    def open_edit_task(
        self,
        task
    ):

        dialog = EditTaskDialog(
            task
        )


        dialog.taskUpdated.connect(
            self.update_task
        )


        dialog.exec()



    def update_task(
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



    # -------------------------
    # LOAD
    # -------------------------

    def load_tasks(self):


        while self.taskLayout.count():

            item = self.taskLayout.takeAt(0)

            widget = item.widget()

            if widget:

                # takeAt() only detaches the widget from layout
                # management — it stays visible at its old geometry
                # until deleteLater()'s deferred delete actually runs.
                # Without hide() here, the previous empty-state label
                # (or a stale TaskCard) can render on top of the fresh
                # content for a frame or more.
                widget.hide()

                widget.deleteLater()



        tasks = self.task_manager.get_all_tasks()



        if self.current_filter != "All":


            if self.current_filter == "Completed":

                tasks = [
                    task
                    for task in tasks
                    if task.completed
                ]


            elif self.current_filter != "Today":

                tasks = [
                    task
                    for task in tasks
                    if task.category == self.current_filter
                ]



        if not tasks:


            theme = ThemeManager.get()


            empty = QLabel(
                "Your day is clear\nAdd something productive."
            )


            empty.setStyleSheet(
                f"""
                QLabel{{

                    color:{theme.Colors.TEXT_SECONDARY};

                    font-size:16px;

                    background:transparent;

                    padding:20px;

                }}
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

                    self.delete_task(
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


        self.update_statistics()



    # -------------------------
    # DELETE
    # -------------------------

    def on_task_completed(
        self,
        task_id,
        checked
    ):

        # Previously this connected straight to task_manager.complete_task
        # and stopped there, so the checkbox itself animated but the stat
        # cards (Today's Tasks / Completed / Pending) and the streak never
        # moved until some other action (add/edit/delete) forced a reload.

        self.task_manager.complete_task(
            task_id,
            checked
        )


        self.update_statistics()



    def delete_task(
        self,
        task
    ):

        # Snapshotted before the delete, so an Undo on the toast can
        # recreate the same task — remove_task() actually deletes the
        # row, there's no separate "trash" to restore from.

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



    # -------------------------
    # STATS
    # -------------------------

    def update_statistics(self):

        stats = self.task_manager.get_statistics()


        self.todayCard.valueLabel.setText(
            str(stats["total"])
        )


        self.completedCard.valueLabel.setText(
            str(stats["completed"])
        )


        self.pendingCard.valueLabel.setText(
            str(stats["pending"])
        )


        self.streakCard.valueLabel.setText(
            f"{stats['streak']} Days"
        )


        # The sidebar's "Today's Progress" ring was never actually
        # wired to real data before — it sat hardcoded at 0%. Compute
        # and broadcast it here so app.py can push it into the ring.
        total = stats["total"]

        percent = (
            round((stats["completed"] / total) * 100)
            if total
            else 0
        )

        self.progressChanged.emit(percent)


        goal = self._weekly_goal()

        self.weeklyCard.refresh(
            self.task_manager.get_week_completion(goal)
        )


    def _weekly_goal(self):

        try:

            return max(1, int(self.settings_manager.get("weekly_goal", "35")))

        except (TypeError, ValueError):

            return 35
