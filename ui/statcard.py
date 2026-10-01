from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget

from themes.manager import ThemeManager
from utils.color_utils import lighten, rgba
from utils.glass_effects import RefractiveGlassMixin, apply_soft_shadow
from ui.icons import IconGlyph


class IconBadge(QWidget):

    # The round icon at the top of a stat card. Two looks, chosen by the
    # theme's Style.ICON_STYLE:
    #   "solid" - a filled accent disc with a white glyph (original look)
    #   "ring"  - a tinted disc, a crisp accent ring and a soft halo
    #             around it, with the glyph in a light shade of the accent
    #
    # The halo is painted here (radial gradient) rather than done with a
    # QGraphicsEffect, because the card that owns this badge already has a
    # shadow effect and Qt doesn't like effects nested inside effects.

    SIZE = 56

    DISC = 44

    def __init__(self, icon, parent=None):

        super().__init__(parent)

        self.setFixedSize(self.SIZE, self.SIZE)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self._accent = QColor("#5A7DFF")

        self._ring = False

        self._glow = 0.0

        offset = (self.SIZE - 20) // 2

        self.glyph = IconGlyph(
            icon,
            size=20,
            color="white",
            stroke_width=2.0,
            parent=self
        )

        self.glyph.move(offset, offset)

    def configure(self, accent, ring, glow):

        self._accent = QColor(accent)

        self._ring = ring

        self._glow = glow

        self.glyph.setColor(
            lighten(accent, 125) if ring else "white"
        )

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = QPointF(self.SIZE / 2, self.SIZE / 2)

        if self._ring:

            if self._glow > 0:

                halo = QRadialGradient(center, self.SIZE / 2)

                inner = QColor(self._accent)

                inner.setAlphaF(0.34 * self._glow)

                outer = QColor(self._accent)

                outer.setAlpha(0)

                halo.setColorAt(0.55, inner)

                halo.setColorAt(1.0, outer)

                painter.setPen(Qt.PenStyle.NoPen)

                painter.setBrush(halo)

                painter.drawEllipse(center, self.SIZE / 2, self.SIZE / 2)

            fill = QColor(self._accent)

            fill.setAlphaF(0.16)

            edge = QColor(self._accent)

            edge.setAlphaF(0.9)

            painter.setPen(QPen(edge, 1.6))

            painter.setBrush(fill)

            painter.drawEllipse(
                center,
                self.DISC / 2 - 0.8,
                self.DISC / 2 - 0.8
            )

        else:

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(self._accent)

            painter.drawEllipse(
                center,
                self.DISC / 2,
                self.DISC / 2
            )


class StatCard(RefractiveGlassMixin, QFrame):

    glass_radius = 20

    def __init__(
        self,
        title,
        value,
        subtitle="",
        icon="check",
        color=None,
        accent_index=0
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
        self.accentIndex = accent_index

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            16,
            12,
            20,
            18
        )

        layout.setSpacing(2)

        topRow = QHBoxLayout()

        topRow.setSpacing(8)

        # A hand-drawn vector icon centered in a round badge — not an
        # emoji character. See ui/icons.py.

        self.iconBadge = IconBadge(icon)

        self.iconGlyph = self.iconBadge.glyph

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

    def _accent(self, theme, style):

        # Themes with Style.STAT_ACCENTS give each card its own colour
        # (blue / green / amber / violet); older themes use one accent
        # for all four, as before.

        if style.STAT_ACCENTS:

            key = style.STAT_ACCENTS[
                self.accentIndex % len(style.STAT_ACCENTS)
            ]

            return getattr(theme.Colors, key)

        return (
            self.valueColor
            if self.valueColor
            else theme.Colors.PRIMARY
        )

    def apply_theme(self):

        theme = ThemeManager.get()

        style = ThemeManager.style()

        accent = self._accent(theme, style)

        tint = style.CARD_TINT

        if tint > 0:

            background = (
                "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                f"stop:0 {rgba(accent, tint)}, "
                f"stop:0.65 {rgba(accent, tint * 0.30)}, "
                f"stop:1 {rgba(accent, tint * 0.10)})"
            )

            border = rgba(accent, 0.30)

        else:

            background = theme.Colors.GLASS

            border = theme.Colors.BORDER

        self.setStyleSheet(
            f"""
            QFrame#statCard{{

                background:{background};

                border:1px solid {border};

                border-radius:20px;

            }}
            """
        )

        self.iconBadge.configure(
            accent,
            ring=(style.ICON_STYLE == "ring"),
            glow=style.GLOW
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

        subtitle_color = (
            lighten(accent, 120)
            if style.ICON_STYLE == "ring" and tint > 0
            else theme.Colors.TEXT_SECONDARY
        )

        self.subtitleLabel.setStyleSheet(
            f"""
            QLabel{{

                color:{subtitle_color};

                font-size:12px;

                background:transparent;

                border:none;

            }}
            """
        )
