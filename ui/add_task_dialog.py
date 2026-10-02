from PySide6.QtCore import Signal

from ui.task_form_dialog import TaskFormDialog


class AddTaskDialog(TaskFormDialog):
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
        bool,
    )

    def __init__(self, parent=None):
        super().__init__(
            "Create Task",
            "Capture the task quickly. Keep the details useful.",
            "Create Task",
            parent=parent,
        )

        self.actionButton.clicked.connect(self.create_task)

    def create_task(self):
        if not self.validate():
            return

        data = self.values()

        self.taskCreated.emit(
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
