import math
import random

from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QGridLayout, QWidget

from themes.manager import ThemeManager
from utils.color_utils import parse_color
from ui.icons import _ICONS


def _paint_icon(painter, name, rect, color, width=1.6):

    # Reuse the app's hand-drawn vector glyphs at an arbitrary spot.

    draw = _ICONS.get(name)

    if draw is None:

        return

    painter.save()

    painter.translate(rect.topLeft())

    pen = QPen(color, width)

    pen.setCapStyle(Qt.PenCapStyle.RoundCap)

    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    painter.setPen(pen)

    painter.setBrush(Qt.BrushStyle.NoBrush)

    draw(painter, rect.width(), rect.height(), color)

    painter.restore()


def _with_alpha(color, alpha):

    c = parse_color(color)

    c.setAlphaF(max(0.0, min(1.0, alpha)))

    return c


class ThemeCard(QWidget):

    # One selectable theme: a miniature of the real UI painted from that
    # theme's own palette, style and atmosphere (so it can never drift out
    # of sync with what you'll actually get), plus its name and tagline.

    clicked = Signal(str)

    PREVIEW_HEIGHT = 68

    def __init__(self, name, parent=None):

        super().__init__(parent)

        self.name = name

        self._selected = False

        self._hover = False

        self.setFixedHeight(126)

        self.setMinimumWidth(118)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setMouseTracking(True)

        self.setToolTip(
            f"{ThemeManager.label(name)} - {ThemeManager.description(name)}"
        )

    def setSelected(self, selected):

        if selected != self._selected:

            self._selected = selected

            self.update()

    def enterEvent(self, event):

        self._hover = True

        self.update()

        super().enterEvent(event)

    def leaveEvent(self, event):

        self._hover = False

        self.update()

        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):

        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):

            self.clicked.emit(self.name)

        super().mouseReleaseEvent(event)

    # -----------------------------------------------------

    def _paint_preview(self, p, r):

        theme = ThemeManager.themes[self.name]

        C = theme.Colors

        atmosphere = ThemeManager.atmosphere(self.name)

        style = ThemeManager.style(self.name)

        rng = random.Random(sum(ord(ch) for ch in self.name) * 7919)

        p.save()

        clip = QPainterPath()

        clip.addRoundedRect(r, 11, 11)

        p.setClipPath(clip)

        # -- sky

        sky = QLinearGradient(r.topLeft(), r.bottomLeft())

        sky.setColorAt(0.0, parse_color(C.SECONDARY))

        sky.setColorAt(1.0, parse_color(C.BACKGROUND))

        p.fillRect(r, sky)

        p.setPen(Qt.PenStyle.NoPen)

        blobs = list(atmosphere.BLOBS[:3])

        if not blobs and atmosphere.KIND == "sakura":

            # Sakura's petals are drawn procedurally elsewhere; hint at its
            # pink haze here.

            pink = parse_color(C.PRIMARY)

            blobs = [
                (pink.red(), pink.green(), pink.blue(), 46, 460, 0.20, 0.30, 0, 0, 0),
                (pink.red(), pink.green(), pink.blue(), 34, 380, 0.85, 0.85, 0, 0, 0),
            ]

        for (cr, cg, cb, ca, radius, ox, oy, *_rest) in blobs:

            center = QPointF(
                r.left() + ox * r.width(),
                r.top() + oy * r.height()
            )

            rad = radius / 1550 * r.width() * 2.3

            g = QRadialGradient(center, rad)

            g.setColorAt(0.0, QColor(cr, cg, cb, min(255, int(ca * 2.4))))

            g.setColorAt(1.0, QColor(cr, cg, cb, 0))

            p.setBrush(g)

            p.drawEllipse(center, rad, rad)

        # -- aurora ribbons

        for (cr, cg, cb, ca, y, amp, thick, speed, wl, phase, tilt) in atmosphere.RIBBONS[:2]:

            path = QPainterPath()

            for i in range(31):

                fx = i / 30

                px = r.left() + fx * r.width()

                py = r.top() + (
                    y
                    + tilt * (fx - 0.5)
                    + amp * 2.4 * math.sin(fx * math.tau / wl + phase)
                ) * r.height()

                if i == 0:

                    path.moveTo(px, py)

                else:

                    path.lineTo(px, py)

            p.setBrush(Qt.BrushStyle.NoBrush)

            for width, mult in ((7.0, 0.55), (3.0, 1.1)):

                p.setPen(
                    QPen(
                        QColor(cr, cg, cb, min(255, int(ca * mult))),
                        width,
                        Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap
                    )
                )

                p.drawPath(path)

        # -- scene layers for themes that draw their own sky

        if atmosphere.KIND == "astro":

            sun = QPointF(r.left() - r.width() * 0.03, r.top() - r.height() * 0.10)

            glow = QRadialGradient(sun, r.width() * 0.62)

            glow.setColorAt(0.0, QColor(255, 170, 60, 210))

            glow.setColorAt(1.0, QColor(255, 120, 30, 0))

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(glow)

            p.drawEllipse(sun, r.width() * 0.62, r.width() * 0.62)

            p.setBrush(QColor(255, 240, 190, 255))

            p.drawEllipse(sun, r.width() * 0.07, r.width() * 0.07)

            colors = (
                (196, 190, 184), (246, 222, 164), (86, 168, 255), (232, 108, 68),
                (226, 178, 128), (242, 216, 158), (150, 226, 236), (78, 118, 255),
            )

            for i, frac in enumerate((0.15, 0.22, 0.30, 0.38, 0.50, 0.62, 0.74, 0.86)):

                orbit = frac * r.width() * 1.32

                p.setBrush(Qt.BrushStyle.NoBrush)

                p.setPen(QPen(QColor(255, 236, 210, 26), 0.7))

                p.drawEllipse(sun, orbit, orbit)

                angle = math.radians(20 + (i * 17) % 52)

                pos = QPointF(sun.x() + orbit * math.cos(angle), sun.y() + orbit * math.sin(angle))

                p.setPen(Qt.PenStyle.NoPen)

                p.setBrush(QColor(*colors[i]))

                dot = 1.1 + (1.2 if i in (4, 5) else 0.3 * (i % 3))

                p.drawEllipse(pos, dot, dot)

        elif atmosphere.KIND == "synthwave":

            horizon = r.top() + r.height() * 0.58

            centre = QPointF(r.left() + r.width() * 0.64, horizon)

            radius = r.height() * 0.36

            disc = QPainterPath()

            disc.addEllipse(centre, radius, radius)

            above = QPainterPath()

            above.addRect(QRectF(r.left(), r.top(), r.width(), horizon - r.top()))

            sun_gradient = QLinearGradient(0, horizon - radius, 0, horizon)

            sun_gradient.setColorAt(0.0, QColor(255, 226, 70))

            sun_gradient.setColorAt(0.6, QColor(255, 112, 90))

            sun_gradient.setColorAt(1.0, QColor(255, 36, 150))

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(sun_gradient)

            p.drawPath(disc.intersected(above))

            p.setBrush(QColor(14, 4, 26, 235))

            p.drawRect(QRectF(r.left(), horizon, r.width(), r.bottom() - horizon))

            for f in (0.3, 0.62, 1.0):

                yy = horizon + (r.bottom() - horizon) * f ** 1.5

                p.setPen(QPen(QColor(255, 90, 190, 170), 0.7))

                p.drawLine(QPointF(r.left(), yy), QPointF(r.right(), yy))

            for i in range(-6, 7):

                p.setPen(QPen(QColor(190, 130, 255, 130), 0.7))

                p.drawLine(
                    QPointF(centre.x() + i * 2, horizon),
                    QPointF(centre.x() + i * 16, r.bottom())
                )

        # -- particles

        p.setPen(Qt.PenStyle.NoPen)

        tint = atmosphere.PARTICLE_COLOR

        if atmosphere.PARTICLES == "stars" and atmosphere.KIND in ("aurora", "astro", "synthwave"):

            for _ in range(min(16, max(5, atmosphere.PARTICLE_COUNT // 7))):

                p.setBrush(
                    QColor(
                        tint[0], tint[1], tint[2],
                        int(255 * atmosphere.PARTICLE_ALPHA * rng.uniform(0.5, 1.0))
                    )
                )

                p.drawEllipse(
                    QPointF(
                        rng.uniform(r.left() + 4, r.right() - 4),
                        rng.uniform(r.top() + 3, r.bottom() - 3)
                    ),
                    rng.uniform(0.5, 1.1),
                    rng.uniform(0.5, 1.1)
                )

        elif atmosphere.PARTICLES == "bubbles":

            for _ in range(7):

                p.setBrush(Qt.BrushStyle.NoBrush)

                p.setPen(QPen(QColor(tint[0], tint[1], tint[2], 120), 0.8))

                rad = rng.uniform(1.4, 3.2)

                p.drawEllipse(
                    QPointF(
                        rng.uniform(r.left() + 6, r.right() - 6),
                        rng.uniform(r.top() + 6, r.bottom() - 4)
                    ),
                    rad,
                    rad
                )

            p.setPen(Qt.PenStyle.NoPen)

        elif atmosphere.PARTICLES == "embers":

            for _ in range(11):

                px = rng.uniform(r.left() + 5, r.right() - 5)

                py = rng.uniform(r.top() + 5, r.bottom() - 3)

                halo = QRadialGradient(QPointF(px, py), 5)

                halo.setColorAt(0.0, QColor(tint[0], tint[1], tint[2], 120))

                halo.setColorAt(1.0, QColor(tint[0], tint[1], tint[2], 0))

                p.setBrush(halo)

                p.drawEllipse(QPointF(px, py), 5, 5)

                p.setBrush(QColor(255, 236, 190, 230))

                p.drawEllipse(QPointF(px, py), 0.9, 0.9)

        elif atmosphere.PARTICLES == "snow":

            for _ in range(20):

                p.setBrush(QColor(tint[0], tint[1], tint[2], int(rng.uniform(120, 240))))

                rad = rng.uniform(0.7, 1.8)

                p.drawEllipse(
                    QPointF(
                        rng.uniform(r.left() + 3, r.right() - 3),
                        rng.uniform(r.top() + 3, r.bottom() - 3)
                    ),
                    rad,
                    rad
                )

        elif atmosphere.PARTICLES == "fireflies":

            for _ in range(8):

                px = rng.uniform(r.left() + 8, r.right() - 8)

                py = rng.uniform(r.top() + 8, r.bottom() - 6)

                halo = QRadialGradient(QPointF(px, py), 7)

                halo.setColorAt(0.0, QColor(tint[0], tint[1], tint[2], 150))

                halo.setColorAt(1.0, QColor(tint[0], tint[1], tint[2], 0))

                p.setBrush(halo)

                p.drawEllipse(QPointF(px, py), 7, 7)

                p.setBrush(QColor(255, 255, 210, 240))

                p.drawEllipse(QPointF(px, py), 1.1, 1.1)

        elif atmosphere.KIND == "sakura":

            for _ in range(9):

                p.setBrush(_with_alpha(C.PRIMARY, rng.uniform(0.35, 0.8)))

                p.drawEllipse(
                    QPointF(
                        rng.uniform(r.left() + 4, r.right() - 4),
                        rng.uniform(r.top() + 3, r.bottom() - 3)
                    ),
                    1.6,
                    1.2
                )

        # -- miniature sidebar

        side = QRectF(
            r.left() + 5,
            r.top() + 5,
            r.width() * 0.21,
            r.height() - 10
        )

        p.setBrush(_with_alpha(C.SURFACE, 0.55))

        p.setPen(QPen(parse_color(C.BORDER), 0.8))

        p.drawRoundedRect(side, 5, 5)

        p.setPen(Qt.PenStyle.NoPen)

        # logo bar
        p.setBrush(_with_alpha(C.TEXT, 0.75))

        p.drawRoundedRect(
            QRectF(side.left() + 4, side.top() + 5, side.width() * 0.55, 3),
            1.5,
            1.5
        )

        for i in range(3):

            y = side.top() + 15 + i * 8

            if i == 0:

                p.setBrush(_with_alpha(C.PRIMARY, 0.85))

            else:

                p.setBrush(_with_alpha(C.TEXT_SECONDARY, 0.45))

            p.drawRoundedRect(
                QRectF(side.left() + 4, y, side.width() - 8, 4.5),
                2,
                2
            )

        # -- header bar + primary button

        x0 = side.right() + 6

        p.setBrush(_with_alpha(C.TEXT, 0.6))

        p.drawRoundedRect(QRectF(x0, r.top() + 7, 30, 3), 1.5, 1.5)

        p.setBrush(parse_color(C.PRIMARY))

        p.drawEllipse(QPointF(r.right() - 9, r.top() + 9), 4, 4)

        # -- three stat cards

        gap = 4

        card_w = (r.right() - 5 - x0 - 2 * gap) / 3

        for i in range(3):

            card = QRectF(x0 + i * (card_w + gap), r.top() + 17, card_w, 15)

            if style.CARD_TINT > 0 and style.STAT_ACCENTS:

                accent = parse_color(
                    getattr(C, style.STAT_ACCENTS[i % len(style.STAT_ACCENTS)])
                )

                g = QLinearGradient(card.topLeft(), card.bottomRight())

                a0 = QColor(accent)

                a0.setAlphaF(0.55)

                a1 = QColor(accent)

                a1.setAlphaF(0.14)

                g.setColorAt(0.0, a0)

                g.setColorAt(1.0, a1)

                p.setBrush(g)

                p.setPen(QPen(_with_alpha(accent, 0.55), 0.8))

            else:

                p.setBrush(_with_alpha(C.SURFACE, 0.7))

                p.setPen(QPen(parse_color(C.BORDER), 0.8))

            p.drawRoundedRect(card, 4, 4)

        # -- task list panel

        panel = QRectF(x0, r.top() + 36, r.right() - 5 - x0, r.bottom() - 5 - (r.top() + 36))

        p.setBrush(_with_alpha(C.SURFACE, 0.6))

        p.setPen(QPen(parse_color(C.BORDER), 0.8))

        p.drawRoundedRect(panel, 4, 4)

        p.setPen(Qt.PenStyle.NoPen)

        for i in range(2):

            y = panel.top() + 5 + i * 8

            if y + 4 > panel.bottom():

                break

            p.setBrush(_with_alpha(C.TEXT_SECONDARY, 0.55))

            p.drawEllipse(QPointF(panel.left() + 6, y + 2), 2, 2)

            p.setBrush(_with_alpha(C.TEXT, 0.4))

            p.drawRoundedRect(
                QRectF(panel.left() + 12, y, panel.width() * 0.5, 3.4),
                1.7,
                1.7
            )

            p.setBrush(
                _with_alpha(
                    (C.RED, C.GREEN)[i % 2],
                    0.75
                )
            )

            p.drawRoundedRect(
                QRectF(panel.right() - 14, y, 9, 3.4),
                1.7,
                1.7
            )

        p.restore()

    # -----------------------------------------------------

    def paintEvent(self, event):

        active = ThemeManager.get().Colors

        own = ThemeManager.themes[self.name].Colors

        p = QPainter(self)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        card = QRectF(self.rect()).adjusted(1, 1, -1, -1)

        outline = QPainterPath()

        outline.addRoundedRect(card, 16, 16)

        p.fillPath(outline, parse_color(active.GLASS))

        if self._selected:

            pen = QPen(parse_color(own.PRIMARY), 2.0)

        elif self._hover:

            pen = QPen(_with_alpha(active.BORDER_ACTIVE, 0.85), 1.4)

        else:

            pen = QPen(parse_color(active.BORDER), 1.0)

        p.setPen(pen)

        p.setBrush(Qt.BrushStyle.NoBrush)

        p.drawPath(outline)

        preview = QRectF(
            card.left() + 7,
            card.top() + 7,
            card.width() - 14,
            self.PREVIEW_HEIGHT
        )

        self._paint_preview(p, preview)

        # -- selected badge

        if self._selected:

            badge = QPointF(preview.right() - 12, preview.top() + 12)

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(parse_color(own.PRIMARY))

            p.drawEllipse(badge, 8, 8)

            _paint_icon(
                p,
                "check",
                QRectF(badge.x() - 5, badge.y() - 5, 10, 10),
                QColor("white"),
                1.7
            )

        # -- name + tagline

        text_left = card.left() + 14

        icon_rect = QRectF(text_left, preview.bottom() + 11, 15, 15)

        _paint_icon(
            p,
            ThemeManager.icon(self.name),
            icon_rect,
            parse_color(own.PRIMARY) if self._selected else parse_color(active.TEXT),
            1.5
        )

        name_font = QFont(self.font())

        name_font.setPixelSize(13)

        name_font.setWeight(QFont.Weight.Bold)

        p.setFont(name_font)

        p.setPen(parse_color(active.TEXT))

        p.drawText(
            QPointF(icon_rect.right() + 7, icon_rect.bottom() - 1.5),
            ThemeManager.label(self.name)
        )

        tag_font = QFont(self.font())

        tag_font.setPixelSize(11)

        p.setFont(tag_font)

        p.setPen(parse_color(active.TEXT_SECONDARY))

        tag = QFontMetrics(tag_font).elidedText(
            ThemeManager.tagline(self.name),
            Qt.TextElideMode.ElideRight,
            int(card.width() - 26)
        )

        p.drawText(
            QPointF(text_left, icon_rect.bottom() + 17),
            tag
        )

        p.end()


class ThemePicker(QWidget):

    # A row of ThemeCards - one per registered theme, in registry order.
    # Adding a theme module to ThemeManager.themes adds a card here
    # automatically.

    themeSelected = Signal(str)

    COLUMNS = 7

    def __init__(self, parent=None):

        super().__init__(parent)

        grid = QGridLayout(self)

        grid.setContentsMargins(0, 2, 0, 2)

        grid.setHorizontalSpacing(12)

        grid.setVerticalSpacing(12)

        self.cards = {}

        for index, name in enumerate(ThemeManager.names()):

            card = ThemeCard(name)

            card.clicked.connect(self.themeSelected.emit)

            self.cards[name] = card

            grid.addWidget(card, index // self.COLUMNS, index % self.COLUMNS)

        for column in range(self.COLUMNS):

            grid.setColumnStretch(column, 1)

        self.set_current(ThemeManager.current_name)

    def set_current(self, name):

        for key, card in self.cards.items():

            card.setSelected(key == name)

    def refresh(self):

        for card in self.cards.values():

            card.update()
