import sys

from PySide6.QtWidgets import QApplication

from app import Flux

from utils.theme import Theme
from themes.manager import ThemeManager
from utils.settings_manager import SettingsManager

from ui.branding import apply_app_identity



app = QApplication(
    sys.argv
)


apply_app_identity(
    app
)


startup_settings = SettingsManager()
ThemeManager.current_name = startup_settings.get_theme()
startup_settings.close()

app.setStyleSheet(
    Theme.stylesheet()
)


window = Flux()

window.show()


sys.exit(
    app.exec()
)