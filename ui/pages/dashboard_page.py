from PySide6.QtWidgets import QWidget, QVBoxLayout

from ui.dashboard import Dashboard


class DashboardPage(QWidget):

    def __init__(self):

        super().__init__()


        layout = QVBoxLayout(
            self
        )


        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )


        self.dashboard = Dashboard()


        layout.addWidget(
            self.dashboard
        )

    def refresh_theme(self):

        self.dashboard.refresh_theme()
