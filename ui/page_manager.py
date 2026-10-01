from PySide6.QtWidgets import QStackedWidget


class PageManager(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.pages = {}
        self._reduce_motion = False

    def add_page(self, name, widget):
        self.pages[name] = widget
        self.addWidget(widget)

    def set_reduce_motion(self, enabled):
        self._reduce_motion = bool(enabled)

    def show_page(self, name, animate=True):
        if name in self.pages:
            self.setCurrentWidget(self.pages[name])
