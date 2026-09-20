from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame
)

from utils.task_manager import TaskManager
from utils.glass_effects import RefractiveGlassMixin, GlassFrame
from themes.manager import ThemeManager


class StatBox(RefractiveGlassMixin, QFrame):

    glass_radius = 18

    def __init__(
        self,
        title,
        value,
        accent
    ):

        super().__init__()

        self.setObjectName(
            "statBox"
        )

        self.accent = accent


        layout = QVBoxLayout(
            self
        )


        self.nameLabel = QLabel(
            title
        )


        self.value = QLabel(
            str(value)
        )


        layout.addWidget(
            self.nameLabel
        )


        layout.addWidget(
            self.value
        )


        self.apply_theme()



    def apply_theme(self):

        theme = ThemeManager.get()


        self.setStyleSheet(
            f"""
            QFrame#{self.objectName()}{{

                background:{theme.Colors.GLASS};

                border:1px solid {theme.Colors.BORDER};

                border-radius:18px;

            }}
            """
        )


        self.nameLabel.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT_SECONDARY};
            font-size:14px;
            background:transparent;
            border:none;
            """
        )


        self.value.setStyleSheet(
            f"""
            color:{self.accent};
            font-size:30px;
            font-weight:900;
            background:transparent;
            border:1px solid {theme.Colors.BORDER};
            border-radius:14px;
            """
        )



    def set_value(
        self,
        value
    ):

        self.value.setText(
            str(value)
        )



class StatisticsPage(QWidget):

    def __init__(self):

        super().__init__()


        self.manager = TaskManager()


        root = QVBoxLayout(
            self
        )


        root.setContentsMargins(
            0,
            0,
            0,
            0
        )


        root.setSpacing(
            18
        )


        self.title = QLabel(
            "Statistics"
        )


        self.subtitle = QLabel(
            "Track your productivity progress."
        )


        root.addWidget(
            self.title
        )


        root.addWidget(
            self.subtitle
        )



        theme = ThemeManager.get()


        cards = QHBoxLayout()

        cards.setSpacing(
            16
        )


        self.total = StatBox(
            "Today's Tasks",
            0,
            theme.Colors.PRIMARY
        )


        self.completed = StatBox(
            "Completed",
            0,
            theme.Colors.GREEN
        )


        self.pending = StatBox(
            "Pending",
            0,
            theme.Colors.ORANGE
        )


        self.streak = StatBox(
            "Streak",
            "0 Days",
            theme.Colors.PURPLE
        )


        cards.addWidget(self.total)
        cards.addWidget(self.completed)
        cards.addWidget(self.pending)
        cards.addWidget(self.streak)


        root.addLayout(
            cards
        )



        # Activity section

        self.activity = GlassFrame()

        self.activity.setObjectName(
            "activityCard"
        )


        activityLayout = QVBoxLayout(
            self.activity
        )


        self.activityTitle = QLabel(
            "Productivity Overview"
        )


        self.info = QLabel()


        activityLayout.addWidget(
            self.activityTitle
        )


        activityLayout.addWidget(
            self.info
        )


        root.addWidget(
            self.activity
        )


        root.addStretch()


        self.apply_theme()

        self.refresh_stats()



    def apply_theme(self):

        theme = ThemeManager.get()


        self.title.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:32px;
            font-weight:800;
            background:transparent;
            """
        )


        self.subtitle.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT_SECONDARY};
            font-size:15px;
            background:transparent;
            """
        )


        self.activity.setStyleSheet(
            f"""
            QFrame#activityCard{{

                background:{theme.Colors.GLASS};

                border-radius:20px;

                border:1px solid {theme.Colors.BORDER};

            }}
            """
        )


        self.activityTitle.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT};
            font-size:22px;
            font-weight:700;
            background:transparent;
            border:none;
            """
        )


        self.info.setStyleSheet(
            f"""
            color:{theme.Colors.TEXT_SECONDARY};
            font-size:16px;
            background:transparent;
            line-height:1.5;
            border:none;
            """
        )


        for box, accent in (
            (self.total, theme.Colors.PRIMARY),
            (self.completed, theme.Colors.GREEN),
            (self.pending, theme.Colors.ORANGE),
            (self.streak, theme.Colors.PURPLE),
        ):

            box.accent = accent

            box.apply_theme()



    def refresh_stats(self):

        stats = self.manager.get_statistics()


        self.total.set_value(
            stats["total"]
        )


        self.completed.set_value(
            stats["completed"]
        )


        self.pending.set_value(
            stats["pending"]
        )


        self.streak.set_value(
            f'{stats["streak"]} Days'
        )


        self.info.setText(
            f"""Completed tasks: {stats["completed"]}

Pending tasks: {stats["pending"]}

Current streak: {stats["streak"]} days

Keep building consistency"""
        )



    def refresh_theme(self):

        self.apply_theme()

        self.refresh_stats()



    def showEvent(self, event):

        # Same reasoning as TasksPage: this page is constructed once
        # and kept alive for the app's lifetime, so without this its
        # numbers would freeze at whatever they were on first render.

        super().showEvent(event)

        self.refresh_stats()
