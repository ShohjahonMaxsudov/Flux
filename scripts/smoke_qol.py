import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

qa_db = ROOT / "qol_qa_flux.db"
if qa_db.exists():
    qa_db.unlink()

os.environ["FLUX_DB_PATH"] = str(qa_db)
os.environ["QT_QPA_PLATFORM"] = os.environ.get("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from animations.aurora import AuroraBackground
from animations.stars import StarField
from animations.sakura import SakuraBackground
from animations.astro import AstroBackground
from animations.synthwave import SynthwaveBackground
from app import Flux
from utils.habit_manager import HabitManager
from utils.settings_manager import SettingsManager


def main():
    app = QApplication([])

    settings = SettingsManager()
    settings.set_lock_screen_enabled(False)
    settings.close()

    # Background widgets must be idle until Flux explicitly activates them.
    for cls in (
        AuroraBackground,
        StarField,
        SakuraBackground,
        AstroBackground,
        SynthwaveBackground,
    ):
        widget = cls()
        assert not widget.timer.isActive(), f"{cls.__name__} timer auto-started"
        assert widget.timer.timerType() == Qt.TimerType.PreciseTimer
        widget.start()
        assert widget.timer.isActive()
        widget.stop()
        assert not widget.timer.isActive()
        widget.deleteLater()

    manager = HabitManager()
    habit_id = manager.create_habit("QA Habit", "#5A7DFF")
    assert habit_id is not None

    habits = manager.get_habits()
    assert any(item["name"] == "QA Habit" for item in habits)

    today = manager.week_days()[0].strftime("%Y-%m-%d")
    checked = manager.toggle_day(habit_id, today)
    assert checked is True
    assert manager.weekly_completion() > 0
    manager.delete_habit(habit_id)
    manager.close()

    window = Flux()
    window.resize(1280, 780)
    window.show()

    for _ in range(10):
        app.processEvents()

    assert "Habits" in window.pages.pages
    assert "Habits" in window.dock._by_key

    window.change_page("Habits")

    for _ in range(5):
        app.processEvents()

    assert window.pages.currentWidget() is window.habitsPage

    window.habitsPage.name_input.setText("Read 20 min")
    window.habitsPage.create_habit()
    assert any(
        item["name"] == "Read 20 min"
        for item in window.habitsPage.manager.get_habits()
    )

    window.hide()

    for _ in range(5):
        app.processEvents()

    for widget in (
        window.aurora,
        window.stars,
        window.sakura,
        window.astro,
        window.synthwave,
    ):
        assert not widget.timer.isActive(), f"{type(widget).__name__} kept running while hidden"

    window.close()
    app.quit()

    print("Flux QOL 1.0.4 smoke test passed")


if __name__ == "__main__":
    main()
