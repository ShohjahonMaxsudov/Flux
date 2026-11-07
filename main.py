import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app import Flux
from themes.manager import ThemeManager
from ui.branding import apply_app_identity

app = QApplication(sys.argv)
apply_app_identity(app)
app.setFont(QFont("Helvetica", 10))
app.setStyleSheet(ThemeManager.stylesheet())
window = Flux()
window.show()
sys.exit(app.exec())
