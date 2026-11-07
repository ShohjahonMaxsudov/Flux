"""Add / edit / delete / undo for tasks, shared by every page that lists them."""

from ui.add_task_dialog import AddTaskDialog
from ui.edit_task_dialog import EditTaskDialog
from ui.toast import notify


class TaskActions:
    # Mix into a widget that has `self.task_manager` and a `load_tasks()` method.
    def open_add_task(self):
        dialog = AddTaskDialog()
        dialog.taskCreated.connect(self.create_task)
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
        important,
    ):
        # Argument order matches AddTaskDialog.taskCreated's signal.
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
            important=important,
        )

        self.load_tasks()
        notify(f'Added "{title}"' if title else "Task added", "success")

    def open_edit_task(self, task):
        dialog = EditTaskDialog(task)
        dialog.taskUpdated.connect(self.update_task)
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

        self.load_tasks()
        notify(f'Updated "{title}"' if title else "Task updated", "success")

    def delete_task(self, task):
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
            important=task.important,
        )

        was_completed = task.completed
        title = task.title
        self.task_manager.remove_task(task.id)
        self.load_tasks()

        notify(
            f'Deleted "{title}"' if title else "Task deleted",
            "info",
            action=("Undo", lambda: self._undo_delete(snapshot, was_completed)),
        )

    def _undo_delete(self, snapshot, was_completed):
        new_id = self.task_manager.create_task(**snapshot)

        if was_completed and new_id:
            self.task_manager.complete_task(new_id, True)

        self.load_tasks()
        notify("Task restored", "success")
