from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget
)

from utils.glass_effects import GlassFrame
from themes.manager import ThemeManager


class MiniCalendar(GlassFrame):

    # A compact month view for the Dashboard — not the full Calendar
    # page, just "what does this month look like": today highlighted,
    # a small dot under any day that has a task, and prev/next month
    # navigation. Clicking a date asks (via dateActivated) to jump to
    # the full Calendar page focused on that day.

    glass_radius = 20

    dateActivated = Signal(QDate)


    def __init__(self, task_manager):

        super().__init__()

        self.setObjectName("miniCalendar")

        self.task_manager = task_manager

        self.shown_month = QDate.currentDate()


        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 18, 20, 18)

        layout.setSpacing(12)


        header = QHBoxLayout()

        self.prevButton = QPushButton("‹")

        self.prevButton.setFixedSize(28, 28)

        self.prevButton.setCursor(Qt.PointingHandCursor)

        self.prevButton.clicked.connect(self.go_previous_month)


        self.monthLabel = QLabel()

        self.monthLabel.setAlignment(Qt.AlignCenter)


        self.nextButton = QPushButton("›")

        self.nextButton.setFixedSize(28, 28)

        self.nextButton.setCursor(Qt.PointingHandCursor)

        self.nextButton.clicked.connect(self.go_next_month)


        header.addWidget(self.prevButton)

        header.addWidget(self.monthLabel, 1)

        header.addWidget(self.nextButton)

        layout.addLayout(header)


        self.grid = QGridLayout()

        self.grid.setSpacing(4)

        layout.addLayout(self.grid)


        self.apply_theme()

        self.render_month()



    def go_previous_month(self):

        self.shown_month = self.shown_month.addMonths(-1)

        self.render_month()



    def go_next_month(self):

        self.shown_month = self.shown_month.addMonths(1)

        self.render_month()



    def render_month(self):

        while self.grid.count():

            item = self.grid.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()


        theme = ThemeManager.get()


        self.monthLabel.setText(
            self.shown_month.toString("MMMM yyyy")
        )


        for col, label in enumerate(["S", "M", "T", "W", "T", "F", "S"]):

            heading = QLabel(label)

            heading.setAlignment(Qt.AlignCenter)

            heading.setStyleSheet(
                f"color:{theme.Colors.TEXT_SECONDARY}; font-size:11px; "
                "font-weight:700; background:transparent; border:none;"
            )

            self.grid.addWidget(heading, 0, col)


        first_of_month = QDate(
            self.shown_month.year(),
            self.shown_month.month(),
            1
        )

        # QDate.dayOfWeek() is 1=Monday..7=Sunday; this grid starts on
        # Sunday, so shift into a 0=Sunday..6=Saturday offset.
        start_col = first_of_month.dayOfWeek() % 7

        days_in_month = first_of_month.daysInMonth()


        task_dates = set()

        for task in self.task_manager.get_all_tasks():

            if task.task_date:

                d = QDate.fromString(task.task_date, "yyyy-MM-dd")

                if d.isValid() and d.year() == self.shown_month.year() and d.month() == self.shown_month.month():

                    task_dates.add(d.day())


        today = QDate.currentDate()

        row = 1

        col = start_col

        for day in range(1, days_in_month + 1):

            date = QDate(self.shown_month.year(), self.shown_month.month(), day)

            cell = QPushButton(str(day))

            cell.setFixedSize(30, 30)

            cell.setCursor(Qt.PointingHandCursor)

            cell.clicked.connect(
                lambda checked, d=date: self.dateActivated.emit(d)
            )


            is_today = (date == today)

            has_tasks = day in task_dates


            bg = "transparent"

            text_color = theme.Colors.TEXT

            border = "none"

            font_weight = "500"


            if is_today:

                bg = theme.Colors.PRIMARY

                text_color = "white"

                font_weight = "700"

            elif has_tasks:

                border = f"1px solid {theme.Colors.PRIMARY}"

                font_weight = "700"


            cell.setStyleSheet(
                f"""
                QPushButton{{

                    background:{bg};

                    color:{text_color};

                    border:{border};

                    border-radius:15px;

                    font-size:12px;

                    font-weight:{font_weight};

                }}

                QPushButton:hover{{

                    background:{theme.Colors.GLASS_HOVER};

                }}
                """
            )

            self.grid.addWidget(cell, row, col)

            col += 1

            if col > 6:

                col = 0

                row += 1



    def apply_theme(self):

        theme = ThemeManager.get()

        self.setStyleSheet(
            f"""
            QFrame#miniCalendar{{

                background:{theme.Colors.GLASS};

                border:1px solid {theme.Colors.BORDER};

                border-radius:20px;

            }}
            """
        )

        self.monthLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:15px; font-weight:700; "
            "background:transparent; border:none;"
        )

        for btn in (self.prevButton, self.nextButton):

            btn.setStyleSheet(
                f"""
                QPushButton{{

                    background:{theme.Colors.SURFACE_ALT};

                    color:{theme.Colors.TEXT};

                    border:1px solid {theme.Colors.BORDER};

                    border-radius:14px;

                    font-size:14px;

                    font-weight:700;

                }}

                QPushButton:hover{{

                    background:{theme.Colors.GLASS_HOVER};

                }}
                """
            )



    def refresh_theme(self):

        self.apply_theme()

        self.render_month()
