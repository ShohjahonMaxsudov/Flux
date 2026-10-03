import sys

from PySide6.QtGui import QFont
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


# Flux typography: use Helvetica everywhere. On Windows machines where
# Helvetica is not installed, Qt will fall back to the closest available
# system sans-serif instead of crashing.
app.setFont(
    QFont(
        "Helvetica",
        10
    )
)


app.setStyleSheet(
    Theme.stylesheet()
)


window = Flux()

window.show()


sys.exit(
    app.exec()
)