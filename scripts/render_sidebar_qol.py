import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

db = ROOT / "sidebar_qol_preview.db"
if db.exists():
    db.unlink()

os.environ["FLUX_DB_PATH"] = str(db)

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app import Flux
from utils.habit_manager import HabitManager
from utils.settings_manager import SettingsManager
from utils.task_manager import TaskManager


def main():
    app = QApplication([])
    app.setFont(QFont("Helvetica", 10))

    settings = SettingsManager()
    settings.set_lock_screen_enabled(False)
    settings.close()

    manager = HabitManager()

    ids = [
        manager.create_habit("Read 20 minutes", "#5A7DFF"),
        manager.create_habit("Exercise", "#4BE8A5"),
        manager.create_habit("Journal", "#A56EFF"),
        manager.create_habit("No social media", "#FFC857"),
        manager.create_habit("Sleep 8 hours", "#FF6B6B"),
    ]

    week = manager.week_days()

    patterns = (
        (0, 1, 2, 3, 4),
        (0, 2, 4),
        (0, 1, 3),
        (1, 2, 3, 4),
        (0, 1, 2, 3),
    )

    for habit_id, days in zip(ids, patterns):
        for index in days:
            manager.toggle_day(
                habit_id,
                week[index].strftime("%Y-%m-%d")
            )

    manager.close()

    tasks = TaskManager()
    today = datetime.now().date()

    samples = [
        ("Finish Flux polish", 0, "High", "Coding", False),
        ("Review notes", 0, "Normal", "Study", True),
        ("Gym session", 1, "Normal", "Health", False),
        ("Prepare presentation", 3, "High", "Work", False),
        ("Read chapter", -2, "Low", "Personal", True),
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

    window = Flux()
    window.resize(1450, 900)
    window.show()

    window.change_page("Habits")
    window.sidebar.changeFilter("Habits")

    for _ in range(25):
        app.processEvents()

    habits_output = ROOT / "preview-qol-sidebar-habits.png"

    if not window.grab().save(str(habits_output)):
        raise RuntimeError("Could not save QOL Habits preview")

    window.change_page("Calendar")
    window.sidebar.changeFilter("Calendar")

    for _ in range(25):
        app.processEvents()

    calendar_output = ROOT / "preview-qol-calendar.png"

    if not window.grab().save(str(calendar_output)):
        raise RuntimeError("Could not save QOL Calendar preview")

    print(f"saved {habits_output}")
    print(f"saved {calendar_output}")

    window.hide()
    window.close()
    app.quit()


if __name__ == "__main__":
    main()
