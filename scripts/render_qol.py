import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

preview_db = ROOT / "qol_preview_flux.db"
if preview_db.exists():
    preview_db.unlink()

os.environ["FLUX_DB_PATH"] = str(preview_db)
os.environ["QT_QPA_PLATFORM"] = os.environ.get("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app import Flux
from utils.habit_manager import HabitManager
from utils.settings_manager import SettingsManager


def main():
    app = QApplication([])

    settings = SettingsManager()
    settings.set_lock_screen_enabled(False)
    settings.close()

    manager = HabitManager()

    ids = [
        manager.create_habit("Read 20 minutes", "#5A7DFF"),
        manager.create_habit("Exercise", "#4BE8A5"),
        manager.create_habit("Journal", "#A56EFF"),
        manager.create_habit("No social media", "#FFC857"),
    ]

    week = manager.week_days()

    pattern = (
        (0, 1, 2, 3, 4),
        (0, 2, 4),
        (0, 1, 3),
        (1, 2, 3, 4),
    )

    for habit_id, checked_days in zip(ids, pattern):
        for index in checked_days:
            manager.toggle_day(
                habit_id,
                week[index].strftime("%Y-%m-%d")
            )

    manager.close()

    window = Flux()
    window.resize(1360, 820)
    window.show()
    window.change_page("Habits")

    for _ in range(20):
        app.processEvents()

    output = ROOT / "preview-qol-habits.png"

    if not window.grab().save(str(output)):
        raise RuntimeError("Could not save Habits preview")

    print(f"saved {output}")

    window.close()
    app.quit()



if __name__ == "__main__":
    main()
