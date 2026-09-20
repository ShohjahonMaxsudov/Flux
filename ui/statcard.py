from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout

from themes.manager import ThemeManager
from utils.glass_effects import RefractiveGlassMixin, apply_soft_shadow
from ui.icons import IconGlyph



class StatCard(RefractiveGlassMixin, QFrame):

    glass_radius = 20

    def __init__(
        self,
        title,
        value,
        subtitle="",
        icon="check",
        color=None
    ):

        super().__init__()

        self.setObjectName(
            "statCard"
        )


        self.setMinimumHeight(
            140
        )


        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self.valueColor = color



        layout = QVBoxLayout(
            self
        )


        layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        layout.setSpacing(2)


        topRow = QHBoxLayout()

        topRow.setSpacing(14)


        # A hand-drawn vector icon centered in a colored circular
        # badge — not an emoji character. See ui/icons.py.

        self.iconBadge = QFrame()

        self.iconBadge.setFixedSize(44, 44)

        badgeLayout = QHBoxLayout(self.iconBadge)

        badgeLayout.setContentsMargins(0, 0, 0, 0)

        badgeLayout.setAlignment(Qt.AlignCenter)

        self.iconGlyph = IconGlyph(
            icon,
            size=20,
            color="white",
            stroke_width=2.0
        )

        badgeLayout.addWidget(self.iconGlyph)


        self.valueLabel = QLabel(
            value
        )


        topRow.addWidget(
            self.iconBadge
        )

        topRow.addWidget(
            self.valueLabel
        )

        topRow.addStretch()


        self.titleLabel = QLabel(
            title
        )


        self.subtitleLabel = QLabel(
            subtitle
        )


        layout.addLayout(
            topRow
        )

        layout.addStretch()

        layout.addWidget(
            self.titleLabel
        )

        layout.addWidget(
            self.subtitleLabel
        )


        self.apply_theme()

        apply_soft_shadow(self)



    def apply_theme(self):

        theme = ThemeManager.get()


        accent = (
            self.valueColor
            if self.valueColor
            else theme.Colors.PRIMARY
        )


        self.setStyleSheet(
            f"""
            QFrame#statCard{{

                background:{theme.Colors.GLASS};

                border:1px solid {theme.Colors.BORDER};

                border-radius:20px;

            }}
            """
        )


        self.iconBadge.setStyleSheet(
            f"""
            QFrame{{

                background:{accent};

                border-radius:22px;

                border:none;

            }}
            """
        )


        self.valueLabel.setStyleSheet(
            f"""
            QLabel{{

                color:{theme.Colors.TEXT};

                font-size:30px;

                font-weight:800;

                background:transparent;

                border:none;

            }}
            """
        )


        self.titleLabel.setStyleSheet(
            f"""
            QLabel{{

                color:{theme.Colors.TEXT};

                font-size:15px;

                font-weight:600;

                background:transparent;

                border:none;

            }}
            """
        )


        self.subtitleLabel.setStyleSheet(
            f"""
            QLabel{{

                color:{theme.Colors.TEXT_SECONDARY};

                font-size:12px;

                background:transparent;

                border:none;

            }}
            """
        )
