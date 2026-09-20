from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)

from utils.theme import Theme


class ThemeSelector(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Appearance")

        title.setStyleSheet("""
            font-size:24px;
            font-weight:800;
        """)

        layout.addWidget(title)


        themes = [
            ("🌙 Dark", "dark"),
            ("☀️ Light", "light"),
            ("🌸 Sakura", "sakura")
        ]


        for text, name in themes:

            button = QPushButton(text)

            button.setFixedHeight(45)

            button.clicked.connect(
                lambda checked=False, n=name:
                self.change_theme(n)
            )

            layout.addWidget(button)


        layout.addStretch()


    def change_theme(self, name):

        Theme.set(name)

        self.window().setStyleSheet(
            Theme.stylesheet()
        )