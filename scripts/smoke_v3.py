import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

SMOKE_DB = ROOT / "smoke_flux.db"
if SMOKE_DB.exists():
    SMOKE_DB.unlink()

os.environ["FLUX_PREVIEW"] = "1"
os.environ["FLUX_DB_PATH"] = str(SMOKE_DB)

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication

from app import Flux
from themes.manager import ThemeManager
from utils.milestone_manager import MilestoneManager
from utils.notes_manager import NotesManager
from utils.settings_manager import SettingsManager
from utils.task_manager import TaskManager


def main():
    app = QApplication([])
    window = Flux()
    window.resize(1180, 749)
    window.show()

    for _ in range(10):
        app.processEvents()

    assert ThemeManager.names() == ["midnight"], ThemeManager.names()

    expected_pages = (
        "Dashboard",
        "Tasks",
        "Calendar",
        "Notes",
        "Focus",
        "Statistics",
        "Milestones",
        "Settings",
    )

    for page in expected_pages:
        window.change_page(page)
        for _ in range(3):
            app.processEvents()
        assert window.pages.currentWidget() is window.pages.pages[page]

    tasks_page = window.tasksPage
    tasks_page.quick_title.setText("Smoke test task")
    tasks_page.quick_date.setDate(QDate.currentDate())
    tasks_page.quick_priority.setCurrentText("High")
    tasks_page.quick_category.setCurrentText("Coding")
    tasks_page.quick_add()

    task_manager = TaskManager()
    tasks = task_manager.get_all_tasks()
    created = next((task for task in tasks if task.title == "Smoke test task"), None)
    assert created is not None
    assert created.priority == "High"
    assert created.category == "Coding"
    task_manager.close()

    milestones_page = window.milestonesPage
    milestones_page.name_input.setText("Smoke milestone")
    milestones_page.target_input.setValue(50)
    milestones_page._create()

    milestone_manager = MilestoneManager()
    milestones = milestone_manager.all()
    created_milestone = next(
        (item for item in milestones if item["title"] == "Smoke milestone"),
        None,
    )
    assert created_milestone is not None
    assert int(created_milestone["target"]) == 50
    milestone_manager.close()

    settings_page = window.settingsPage
    settings_page.name_input.setText("Flux QA")
    settings_page.save_name()
    settings_page.goal_spin.setValue(21)
    settings_page.focus_goal_spin.setValue(20)

    settings = SettingsManager()
    assert settings.get_user_name() == "Flux QA"
    assert settings.get("weekly_goal") == "21"
    assert settings.get("focus_weekly_goal_minutes") == "1200"
    settings.close()

    notes_page = window.notesPage
    notes_page.create_note()
    notes_page.titleInput.setText("Smoke note")
    notes_page.contentInput.setPlainText("Flux v3 interaction QA")
    notes_page._save_current_note()

    notes = NotesManager()
    assert any(note.title == "Smoke note" for note in notes.get_all_notes())
    notes.close()

    window.focusPage.apply_preset(50, 10)
    assert window.focusPage.focus_minutes == 50
    assert window.focusPage.remaining_seconds == 50 * 60

    window.dashboardPage.dashboard.refresh_data()
    window.statisticsPage.refresh_stats()

    for _ in range(8):
        app.processEvents()

    window.close()
    app.quit()

    print("Flux v3 smoke test passed")


if __name__ == "__main__":
    main()
