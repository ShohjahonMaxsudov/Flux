import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

os.environ["FLUX_PREVIEW"] = "1"
os.environ["FLUX_DB_PATH"] = str((ROOT / "preview_flux.db").resolve())

from PySide6.QtWidgets import QApplication

from app import Flux
from ui.add_task_dialog import AddTaskDialog
from ui.edit_task_dialog import EditTaskDialog
from utils.focus_manager import FocusManager
from utils.habit_manager import HabitManager
from utils.milestone_manager import MilestoneManager
from utils.task_manager import TaskManager


def seed_demo_data():
    tasks = TaskManager()

    if not tasks.get_all_tasks():
        today = datetime.now().date()

        samples = [
            ("Finish project outline", 0, "High", "Work", False),
            ("Review design mockups", 0, "Normal", "Work", False),
            ("Gym session", 0, "Normal", "Health", False),
            ("Read 20 pages", 0, "Low", "Personal", False),
            ("Plan next week", 1, "High", "Planning", False),
            ("Prepare presentation", 2, "Normal", "Work", False),
            ("Book flight to SF", 4, "Low", "Personal", False),
            ("Answer team emails", 0, "Normal", "Work", True),
            ("Organize notes", 0, "Low", "Personal", True),
        ]

        for title, offset, priority, category, completed in samples:
            task_id = tasks.create_task(
                title=title,
                task_date=(today + timedelta(days=offset)).strftime("%Y-%m-%d"),
                priority=priority,
                category=category,
            )
            if completed:
                tasks.complete_task(task_id, True)

    tasks.close()

    focus = FocusManager()
    if focus.get_week_minutes() == 0:
        focus.log_session(60)
        focus.log_session(50)
        focus.log_session(25)
    focus.close()

    habits = HabitManager()
    rows = habits.get_habits_with_week()

    for h_index, habit in enumerate(rows[:5]):
        for d_index, (day, checked) in enumerate(habit["week"]):
            should_be_on = (d_index + h_index) % 3 != 1 and d_index < 5
            if should_be_on != checked:
                habits.toggle_day(habit["id"], day)

    habits.close()

    milestones = MilestoneManager()
    if not milestones.all():
        first = milestones.create("Ship Flux v3", 100, (datetime.now().date() + timedelta(days=12)).strftime("%Y-%m-%d"))
        second = milestones.create("Finish university shortlist", 20, (datetime.now().date() + timedelta(days=24)).strftime("%Y-%m-%d"))
        third = milestones.create("Complete 30 focus sessions", 30, (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d"))
        milestones.set_progress(first, 70)
        milestones.set_progress(second, 8)
        milestones.set_progress(third, 21)
    milestones.close()


def render(window, name):
    app = QApplication.instance()
    window.show()
    window.raise_()
    window.activateWindow()

    for _ in range(20):
        app.processEvents()

    pixmap = window.grab()
    path = Path(name).resolve()

    if not pixmap.save(str(path)):
        raise RuntimeError(f"Could not save {name}")

    print(f"saved {path} ({pixmap.width()}x{pixmap.height()})")


def main():
    seed_demo_data()

    app = QApplication([])

    for page, filename in (
        ("Dashboard", "preview-dashboard.png"),
        ("Tasks", "preview-tasks.png"),
        ("Milestones", "preview-milestones.png"),
        ("Focus", "preview-focus.png"),
        ("Calendar", "preview-calendar.png"),
        ("Notes", "preview-notes.png"),
        ("Statistics", "preview-statistics.png"),
        ("Settings", "preview-settings.png"),
    ):
        window = Flux()
        window.resize(1480, 900)
        window.change_page(page)
        render(window, filename)
        window.close()
        window.deleteLater()
        for _ in range(6):
            app.processEvents()

    add_dialog = AddTaskDialog()
    add_dialog.resize(600, 720)
    render(add_dialog, "preview-add-task.png")
    add_dialog.close()
    add_dialog.deleteLater()

    task_manager = TaskManager()
    sample_task = task_manager.get_all_tasks()[0]
    edit_dialog = EditTaskDialog(sample_task)
    edit_dialog.resize(600, 720)
    render(edit_dialog, "preview-edit-task.png")
    edit_dialog.close()
    edit_dialog.deleteLater()
    task_manager.close()

    for _ in range(6):
        app.processEvents()

    app.quit()


if __name__ == "__main__":
    main()
