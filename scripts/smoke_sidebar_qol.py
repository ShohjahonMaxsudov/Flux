import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

db = ROOT / "sidebar_qol_smoke.db"
if db.exists():
    db.unlink()

os.environ["FLUX_DB_PATH"] = str(db)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app import Flux
from utils.habit_manager import HabitManager
from utils.settings_manager import SettingsManager


def main():
    app = QApplication([])

    settings = SettingsManager()
    settings.set_lock_screen_enabled(False)
    settings.close()

    habits = HabitManager()
    habit_id = habits.create_habit("Smoke habit")
    assert habit_id
    day = habits.week_days()[0].strftime("%Y-%m-%d")
    assert habits.toggle_day(habit_id, day) is True
    assert habits.weekly_completion() > 0
    habits.close()

    window = Flux()
    window.resize(1280, 760)
    window.show()

    for _ in range(10):
        app.processEvents()

    assert "Habits" in window.pages.pages
    assert any(button.key == "Habits" for button in window.sidebar.buttons)

    window.sidebar.changeFilter("Habits")
    for _ in range(5):
        app.processEvents()

    assert window.pages.currentWidget() is window.habitsPage

    window.sidebar.changeFilter("Calendar")
    for _ in range(5):
        app.processEvents()

    assert window.pages.currentWidget() is window.calendarPage
    assert window.calendarPage.calendar.selectedDate().isValid()

    today = window.calendarPage.calendar.selectedDate()
    window.calendarPage.calendar.next_month()
    assert (
        window.calendarPage.calendar._month != today.month()
        or window.calendarPage.calendar._year != today.year()
    )
    window.calendarPage.calendar.go_today()
    assert window.calendarPage.calendar.selectedDate() == today

    active = [
        widget.timer.isActive()
        for widget in (
            window.aurora,
            window.stars,
            window.sakura,
            window.astro,
            window.synthwave,
        )
    ]
    assert sum(active) <= 2

    window.hide()
    for _ in range(5):
        app.processEvents()

    assert not any(
        widget.timer.isActive()
        for widget in (
            window.aurora,
            window.stars,
            window.sakura,
            window.astro,
            window.synthwave,
        )
    )

    window.close()
    app.quit()

    print("Correct QOL sidebar + Habits smoke test passed")


if __name__ == "__main__":
    main()
