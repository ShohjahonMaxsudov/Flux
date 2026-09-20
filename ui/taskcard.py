from PySide6.QtCore import Qt, QDate, QPoint, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
    QGraphicsOpacityEffect,
    QMenu
)

from themes.manager import ThemeManager
from utils.glass_effects import RefractiveGlassMixin



class TaskCard(RefractiveGlassMixin, QFrame):

    glass_radius = 18

    # No apply_soft_shadow() here — TaskCard already uses a
    # QGraphicsOpacityEffect for its entrance fade-in, and a widget can
    # only hold one graphics effect at a time. The refractive border
    # itself is just paintEvent drawing, so it composites fine with
    # that existing fade.

    checkedChanged = Signal(bool)
    deleteClicked = Signal()
    editClicked = Signal()


    def __init__(
        self,
        title: str,
        time: str,
        priority="Normal",
        category="General",
        completed=False,
        color=None,
        important=False,
        task_date=""
    ):

        super().__init__()


        self.accentColor = color

        self.important = important

        self.priority = priority


        self.setMinimumHeight(88)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )


        self.setObjectName(
            "taskCard"
        )


        main = QHBoxLayout(
            self
        )

        main.setContentsMargins(
            18, 14, 14, 14
        )

        main.setSpacing(14)


        # -- circular checkbox: an empty ring when open, a filled
        # accent circle with a checkmark once completed — not the
        # default Qt checkbox indicator, and no longer carries the
        # task title as its own label text.

        self.checkButton = QPushButton("✓")

        self.checkButton.setCheckable(True)

        self.checkButton.setChecked(completed)

        self.checkButton.setFixedSize(28, 28)

        self.checkButton.setCursor(Qt.PointingHandCursor)

        self.checkButton.toggled.connect(self.on_checked)

        main.addWidget(
            self.checkButton,
            alignment=Qt.AlignTop
        )


        # -- title (own row) + time/pills (row below), matching the
        # reference's two-line layout instead of packing everything
        # onto the checkbox's own label.

        textCol = QVBoxLayout()

        textCol.setSpacing(6)


        titleText = (
            f"★ {title}"
            if important
            else title
        )

        self.titleLabel = QLabel(titleText)


        bottomRow = QHBoxLayout()

        bottomRow.setSpacing(8)


        timeText = time or ""

        if task_date:

            display_date = QDate.fromString(
                task_date,
                "yyyy-MM-dd"
            )

            if display_date.isValid() and display_date != QDate.currentDate():

                timeText = (
                    f"{display_date.toString('MMM d')} • {timeText}"
                    if timeText
                    else display_date.toString('MMM d')
                )


        self.timeLabel = QLabel(timeText)


        self.priorityPill = QLabel(priority)

        self.categoryPill = QLabel(category)


        bottomRow.addWidget(self.timeLabel)

        bottomRow.addWidget(self.priorityPill)

        bottomRow.addWidget(self.categoryPill)

        bottomRow.addStretch()


        textCol.addWidget(self.titleLabel)

        textCol.addLayout(bottomRow)


        main.addLayout(textCol, 1)


        # -- a single overflow menu instead of separate always-visible
        # edit/delete buttons, matching the reference's "⋮" affordance.

        self.menuButton = QPushButton("⋮")

        self.menuButton.setFixedSize(32, 32)

        self.menuButton.setCursor(Qt.PointingHandCursor)

        self.menuButton.clicked.connect(
            self.show_menu
        )

        main.addWidget(
            self.menuButton,
            alignment=Qt.AlignTop
        )


        self.apply_theme()


        if completed:

            self.apply_completed_style(True)


        effect = QGraphicsOpacityEffect(self)

        self.setGraphicsEffect(effect)

        self.fade = QPropertyAnimation(effect, b"opacity")

        self.fade.setDuration(350)

        self.fade.setStartValue(0)

        self.fade.setEndValue(1)

        self.fade.setEasingCurve(QEasingCurve.OutCubic)

        self.fade.start()



    def show_menu(self):

        theme = ThemeManager.get()

        menu = QMenu(self)

        menu.setStyleSheet(
            f"""
            QMenu{{
                background:{theme.Colors.SURFACE};
                color:{theme.Colors.TEXT};
                border:1px solid {theme.Colors.BORDER};
                border-radius:10px;
                padding:6px;
            }}
            QMenu::item{{
                padding:8px 20px;
                border-radius:6px;
            }}
            QMenu::item:selected{{
                background:{theme.Colors.PRIMARY};
                color:white;
            }}
            """
        )

        edit_action = menu.addAction("Edit")

        delete_action = menu.addAction("Delete")


        chosen = menu.exec(
            self.menuButton.mapToGlobal(
                QPoint(0, self.menuButton.height())
            )
        )


        if chosen == edit_action:

            self.editClicked.emit()


        elif chosen == delete_action:

            self.deleteClicked.emit()



    def apply_theme(self):

        theme = ThemeManager.get()


        accent = self.accentColor or theme.Colors.PRIMARY

        priority_color = {
            "High": theme.Colors.RED,
            "Normal": theme.Colors.ORANGE,
            "Low": theme.Colors.GREEN
        }.get(self.priority, theme.Colors.ORANGE)


        self.setStyleSheet(
            f"""

            #taskCard {{

                background:{theme.Colors.GLASS};

                border:1px solid {theme.Colors.BORDER};

                border-radius:18px;

            }}


            #taskCard:hover {{

                background:{theme.Colors.GLASS_HOVER};

                border:1px solid {theme.Colors.BORDER_ACTIVE};

            }}

            """
        )


        self.checkButton.setStyleSheet(
            f"""
            QPushButton{{

                border-radius:14px;

                border:2px solid {theme.Colors.TEXT};

                background:transparent;

                color:transparent;

                font-size:13px;

                font-weight:900;

            }}

            QPushButton:checked{{

                background:{theme.Colors.PRIMARY};

                border:2px solid {theme.Colors.PRIMARY};

                color:white;

            }}
            """
        )


        self.titleLabel.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:15px;
            font-weight:600;
            background:transparent;
            border:none;
            """
        )


        self.timeLabel.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT_SECONDARY};
            font-size:12px;
            background:transparent;
            border:none;
            """
        )


        pill_base = (
            "border-radius:10px; padding:3px 10px; "
            "font-size:11px; font-weight:700; border:none;"
        )

        self.priorityPill.setStyleSheet(
            f"background:{priority_color}; color:white; {pill_base}"
        )

        self.categoryPill.setStyleSheet(
            f"background:{accent}; color:white; {pill_base}"
        )


        self.menuButton.setStyleSheet(
            f"""
            QPushButton {{

                background:transparent;

                border:none;

                color:{theme.Colors.TEXT_SECONDARY};

                font-size:18px;

                font-weight:900;

                border-radius:10px;

            }}

            QPushButton:hover {{

                background:{theme.Colors.GLASS_HOVER};

                color:{theme.Colors.TEXT};

            }}
            """
        )



    def on_checked(
        self,
        checked
    ):

        self.apply_completed_style(
            checked
        )


        self.checkedChanged.emit(
            checked
        )



    def apply_completed_style(
        self,
        checked
    ):

        theme = ThemeManager.get()


        if checked:

            self.titleLabel.setStyleSheet(
                f"""
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:15px;
                font-weight:600;
                text-decoration:line-through;
                background:transparent;
                border:none;
                """
            )


        else:

            self.titleLabel.setStyleSheet(
                f"""
                color:{theme.Colors.TEXT};
                font-size:15px;
                font-weight:600;
                background:transparent;
                border:none;
                """
            )
