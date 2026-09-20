from PySide6.QtWidgets import QStackedWidget


class PageManager(QStackedWidget):

    def __init__(self):

        super().__init__()

        self.pages = {}


    def add_page(
        self,
        name,
        widget
    ):

        self.pages[name] = widget

        self.addWidget(
            widget
        )


    def show_page(
        self,
        name
    ):

        if name in self.pages:

            self.setCurrentWidget(
                self.pages[name]
            )