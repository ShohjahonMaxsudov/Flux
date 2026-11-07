"""Base class for the Create / Edit task dialogs, which share the same look."""

from PySide6.QtWidgets import QDialog

from themes.manager import ThemeManager


class TaskDialog(QDialog):
    # Expects `self.title` (the big heading label) to exist before this runs.
    def apply_theme(self):
        theme = ThemeManager.get()

        self.setStyleSheet(f"""
            QDialog{{
                background:{theme.Colors.BACKGROUND};
            }}
            QLabel{{
                color:{theme.Colors.TEXT};
                background:transparent;
                font-size:14px;
            }}
            QLineEdit,
            QTextEdit,
            QDateEdit,
            QTimeEdit,
            QComboBox{{
                background:{theme.Colors.SURFACE_ALT};
                color:{theme.Colors.TEXT};
                border:1px solid {theme.Colors.BORDER};
                border-radius:12px;
                padding:10px;
            }}
            QTextEdit{{
                min-height:90px;
            }}
            QComboBox QAbstractItemView{{
                background:{theme.Colors.SURFACE};
                color:{theme.Colors.TEXT};
                selection-background-color:{theme.Colors.PRIMARY};
            }}
            QPushButton{{
                background:{theme.Colors.PRIMARY};
                color:white;
                border-radius:14px;
                padding:14px;
                font-size:15px;
                font-weight:700;
            }}
            QPushButton:hover{{
                background:{theme.Colors.BORDER_ACTIVE};
            }}
            QCheckBox{{
                color:{theme.Colors.TEXT};
                font-size:14px;
            }}
            """)

        self.title.setStyleSheet(f"""
            QLabel{{
                color:{theme.Colors.TEXT};
                font-size:28px;
                font-weight:900;
            }}
            """)
