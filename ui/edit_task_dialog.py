from PySide6.QtCore import Signal

from ui.task_form_dialog import TaskFormDialog


class EditTaskDialog(TaskFormDialog):
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
        bool,
    )

    def __init__(self, task, parent=None):
        self.task = task

        super().__init__(
            "Edit Task",
            "Update the task without losing context.",
            "Save Changes",
            task=task,
            parent=parent,
        )

        self.actionButton.clicked.connect(self.save_task)

    def save_task(self):
        if not self.validate():
            return

        data = self.values()

        self.taskUpdated.emit(
            self.task.id,
            data["title"],
            data["time"],
            data["priority"],
            data["category"],
            data["task_date"],
            data["description"],
            data["color"],
            data["reminder"],
            data["repeat"],
            data["important"],
        )

        self.accept()
