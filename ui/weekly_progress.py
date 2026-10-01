from datetime import datetime

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from themes.manager import ThemeManager
from utils.color_utils import lighten, rgba, qcolor
from utils.glass_effects import RefractiveGlassMixin, apply_soft_shadow
from ui.progress_ring import ProgressRing


_DAY_LABELS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


class _WeekBars(QWidget):

    # The bar chart itself, hand-painted rather than built from seven
    # QFrames — makes the "today" highlight and the value-proportional
    # heights easy to keep in one place.

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setMinimumHeight(120)

        self._counts = [0] * 7

        self._today = datetime.now().weekday()

        self._accent = QColor("#5A7DFF")

        self._track = QColor(255, 255, 255, 30)

        self._text = QColor("white")

        self._text_dim = QColor(255, 255, 255, 140)

    def set_counts(self, counts):

        self._counts = list(counts)

        self._today = datetime.now().weekday()

        self.update()

    def set_colors(self, accent, track, text, text_dim):

        self._accent = QColor(accent)

        self._track = QColor(track)

        self._text = QColor(text)

        self._text_dim = QColor(text_dim)

        self.update()

    def paintEvent(self, event):

        p = QPainter(self)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()

        h = self.height()

        label_h = 18

        top_pad = 20

        chart_h = h - label_h - top_pad

        n = len(self._counts)

        gap = 14

        bar_w = (w - gap * (n - 1)) / n

        peak = max(self._counts + [1])

        p.setPen(Qt.PenStyle.NoPen)

        for i, count in enumerate(self._counts):

            x = i * (bar_w + gap)

            is_today = (i == self._today)

            frac = count / peak if peak else 0.0

            bar_h = max(6.0, chart_h * frac)

            # track (full-height, faint) so a zero day still reads as a
            # column rather than empty space
            p.setBrush(self._track)

            p.drawRoundedRect(
                QRectF(x, top_pad, bar_w, chart_h),
                bar_w / 2,
                bar_w / 2
            )

            fill_rect = QRectF(
                x,
                top_pad + (chart_h - bar_h),
                bar_w,
                bar_h
            )

            if is_today:

                gradient = QLinearGradient(0, fill_rect.top(), 0, fill_rect.bottom())

                gradient.setColorAt(0.0, lighten(self._accent.name(), 130))

                gradient.setColorAt(1.0, self._accent)

                p.setBrush(gradient)

            else:

                tinted = QColor(self._accent)

                tinted.setAlpha(150)

                p.setBrush(tinted)

            p.drawRoundedRect(fill_rect, bar_w / 2, bar_w / 2)

            if count > 0:

                p.setPen(self._text if is_today else self._text_dim)

                p.drawText(
                    QRectF(x, fill_rect.top() - 16, bar_w, 14),
                    Qt.AlignmentFlag.AlignCenter,
                    str(count)
                )

                p.setPen(Qt.PenStyle.NoPen)

            p.setPen(self._text if is_today else self._text_dim)

            font = p.font()

            font.setBold(is_today)

            p.setFont(font)

            p.drawText(
                QRectF(x, h - label_h, bar_w, label_h),
                Qt.AlignmentFlag.AlignCenter,
                _DAY_LABELS[i]
            )

            p.setPen(Qt.PenStyle.NoPen)

        p.end()


class WeeklyProgressCard(RefractiveGlassMixin, QFrame):

    glass_radius = 22

    def __init__(self):

        super().__init__()

        self.setObjectName("weeklyProgressCard")

        self.setMinimumWidth(260)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 18, 20, 18)

        layout.setSpacing(10)

        self.titleLabel = QLabel("Weekly Progress")

        layout.addWidget(self.titleLabel)

        self.bars = _WeekBars()

        layout.addWidget(self.bars, 1)

        goalRow = QHBoxLayout()

        goalRow.setSpacing(16)

        self.ring = ProgressRing(diameter=76, thickness=7)

        goalRow.addWidget(self.ring)

        textCol = QVBoxLayout()

        textCol.setSpacing(2)

        self.goalTitle = QLabel("Weekly Goal")

        self.goalValue = QLabel("0 / 0 tasks")

        textCol.addStretch()

        textCol.addWidget(self.goalTitle)

        textCol.addWidget(self.goalValue)

        textCol.addStretch()

        goalRow.addLayout(textCol, 1)

        layout.addLayout(goalRow)

        self.apply_theme()

        apply_soft_shadow(self)

    def refresh(self, data):

        self.bars.set_counts(data["counts"])

        self.ring.setValue(data["percent"])

        self.goalValue.setText(
            f'{data["total"]} / {data["goal"]} tasks'
        )

    def apply_theme(self):

        theme = ThemeManager.get()

        style = ThemeManager.style()

        accent = theme.Colors.PRIMARY

        if style.PANEL_TINT:

            background = (
                "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                f"stop:0 {rgba(accent, 0.14)}, "
                f"stop:1 {rgba(theme.Colors.PURPLE, 0.06)})"
            )

            border = rgba(accent, 0.26)

        else:

            background = theme.Colors.GLASS

            border = theme.Colors.BORDER

        self.setStyleSheet(
            f"""
            QFrame#weeklyProgressCard{{

                background:{background};

                border:1px solid {border};

                border-radius:22px;

            }}
            """
        )

        self.titleLabel.setStyleSheet(
            f"""
            QLabel{{
                color:{theme.Colors.TEXT};
                font-size:17px;
                font-weight:800;
                background:transparent;
                border:none;
            }}
            """
        )

        self.goalTitle.setStyleSheet(
            f"""
            QLabel{{
                color:{theme.Colors.TEXT};
                font-size:13px;
                font-weight:700;
                background:transparent;
                border:none;
            }}
            """
        )

        self.goalValue.setStyleSheet(
            f"""
            QLabel{{
                color:{theme.Colors.TEXT_SECONDARY};
                font-size:12px;
                background:transparent;
                border:none;
            }}
            """
        )

        self.bars.set_colors(
            accent,
            qcolor(theme.Colors.TEXT, 0.10),
            theme.Colors.TEXT,
            theme.Colors.TEXT_SECONDARY
        )

        self.ring.setColors(
            accent,
            qcolor(theme.Colors.TEXT, 0.14),
            theme.Colors.TEXT
        )
