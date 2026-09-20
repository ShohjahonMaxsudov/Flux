import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app import Flux

from utils.theme import Theme


def resource_path(relative_path):
    """
    Absolute path to a bundled resource. Works when running from
    source and when frozen by PyInstaller, which unpacks bundled
    data files into a temp folder pointed to by sys._MEIPASS.
    """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


app = QApplication(
    sys.argv
)


app.setStyleSheet(
    Theme.stylesheet()
)

app.setWindowIcon(
    QIcon(resource_path(os.path.join("assets", "icon.ico")))
)


window = Flux()

window.setWindowIcon(
    QIcon(resource_path(os.path.join("assets", "icon.ico")))
)

window.show()


sys.exit(
    app.exec()
)