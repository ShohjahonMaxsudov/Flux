import sys

from PySide6.QtWidgets import QApplication

from app import Flux

from utils.theme import Theme

from ui.branding import apply_app_identity



app = QApplication(
    sys.argv
)


apply_app_identity(
    app
)


app.setStyleSheet(
    Theme.stylesheet()
)


window = Flux()

window.show()


sys.exit(
    app.exec()
)