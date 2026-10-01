import math
import random
from datetime import date

from PySide6.QtCore import (
    Qt,
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
)

from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
    QRadialGradient,
)

from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from themes.manager import ThemeManager
from utils.color_utils import rgba
from utils.glass_effects import RefractiveGlassMixin
from ui.icons import IconGlyph


QUOTES = [
    "Discipline today, freedom tomorrow.",
    "Small steps create big results.",
    "Progress, not perfection.",
    "One task at a time.",
    "Make today count.",
    "Done is better than perfect.",
    "Focus on the next right thing.",
    "Consistency beats intensity.",
]


class QuoteBanner(RefractiveGlassMixin, QFrame):

    # The strip at the bottom of the dashboard: a daily quote over a small
    # painted landscape that follows the theme's Atmosphere.BANNER -
    # "mountains" (Dark / Nebula / Sakura), "wave" (Void), "ocean"
    # (Ocean) or "plain" (Light). The arrow flips to the next quote.
    #
    # The scene is painted once into a cached pixmap: the animated
    # background underneath forces this widget to repaint every frame,
    # and re-tracing polygons at 60fps for a static picture would be
    # wasted work.

    glass_radius = 22

    def __init__(self):

        super().__init__()

        self.setObjectName("quoteBanner")

        self.setFixedHeight(92)

        self._index = date.today().toordinal() % len(QUOTES)

        self._cache_key = None

        self._cache = None

        row = QHBoxLayout(self)

        row.setContentsMargins(30, 0, 22, 0)

        row.setSpacing(16)

        self.quoteLabel = QLabel(QUOTES[self._index])

        self._quote_effect = QGraphicsOpacityEffect(self.quoteLabel)

        self._quote_effect.setOpacity(1.0)

        self.quoteLabel.setGraphicsEffect(self._quote_effect)

        self.nextButton = QPushButton("")

        self.nextButton.setFixedSize(42, 42)

        self.nextButton.setCursor(Qt.CursorShape.PointingHandCursor)

        self.nextButton.setToolTip("Next quote")

        buttonLayout = QHBoxLayout(self.nextButton)

        buttonLayout.setContentsMargins(0, 0, 0, 0)

        buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.arrow = IconGlyph(
            "arrow_right",
            size=18,
            color="white",
            stroke_width=2.0
        )

        self.arrow.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        buttonLayout.addWidget(self.arrow)

        self.nextButton.clicked.connect(self.next_quote)

        row.addWidget(self.quoteLabel)

        row.addStretch()

        row.addWidget(self.nextButton)

        self.apply_theme()

    # -----------------------------------------------------

    def next_quote(self):

        fade_out = QPropertyAnimation(self._quote_effect, b"opacity", self)

        fade_out.setDuration(140)

        fade_out.setStartValue(1.0)

        fade_out.setEndValue(0.0)

        def swap():

            self._index = (self._index + 1) % len(QUOTES)

            self.quoteLabel.setText(QUOTES[self._index])

            fade_in = QPropertyAnimation(self._quote_effect, b"opacity", self)

            fade_in.setDuration(260)

            fade_in.setStartValue(0.0)

            fade_in.setEndValue(1.0)

            fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

            fade_in.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        fade_out.finished.connect(swap)

        fade_out.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    # -----------------------------------------------------

    def apply_theme(self):

        theme = ThemeManager.get()

        style = ThemeManager.style()

        self._cache_key = None

        self.setStyleSheet(
            f"""
            QFrame#quoteBanner{{

                background:transparent;

                border:1px solid {theme.Colors.BORDER};

                border-radius:22px;

            }}
            """
        )

        self.quoteLabel.setStyleSheet(
            f"""
            QLabel{{

                color:{theme.Colors.TEXT};

                font-size:18px;

                font-weight:500;

                background:transparent;

                border:none;

            }}
            """
        )

        self.arrow.setColor(theme.Colors.TEXT)

        self.nextButton.setStyleSheet(
            f"""
            QPushButton{{

                background:{theme.Colors.GLASS_HOVER};

                border:1px solid {theme.Colors.BORDER};

                border-radius:21px;

            }}

            QPushButton:hover{{

                background:{rgba(theme.Colors.PRIMARY, 0.45)};

                border:1px solid {rgba(theme.Colors.PRIMARY, 0.8)};

            }}
            """
        )

        self.update()

    # -----------------------------------------------------
    # SCENE
    # -----------------------------------------------------

    def _ridge(self, x0, x1, base, amp, seed, height):

        points = []

        steps = 64

        for i in range(steps + 1):

            fx = i / steps

            v = (
                abs(math.sin(fx * 6.5 + seed)) * 0.62
                + abs(math.sin(fx * 15.0 + seed * 2.3)) * 0.28
                + abs(math.sin(fx * 31.0 + seed * 4.1)) * 0.10
            )

            points.append(
                QPointF(x0 + (x1 - x0) * fx, base - amp * v)
            )

        points.append(QPointF(x1, height))

        points.append(QPointF(x0, height))

        return QPolygonF(points)

    def _fade_in_brush(self, x0, x1, color, alpha):

        # Horizontal gradient that eases a shape in from the left, so the
        # landscape melts into the quote text instead of starting on a
        # hard edge.

        gradient = QLinearGradient(x0, 0, x1, 0)

        clear = QColor(color)

        clear.setAlpha(0)

        solid = QColor(color)

        solid.setAlphaF(alpha)

        gradient.setColorAt(0.0, clear)

        gradient.setColorAt(0.30, solid)

        gradient.setColorAt(1.0, solid)

        return gradient

    def _faded_layer(self, p, w, h, dpr, x0, paint, ramp=0.30):

        # Paint a scene element onto its own layer, ease it in from the
        # left (DestinationIn), then composite it. This is what lets the
        # landscape melt into the quote text instead of starting on a
        # hard edge.

        layer = QPixmap(round(w * dpr), round(h * dpr))

        layer.setDevicePixelRatio(dpr)

        layer.fill(Qt.GlobalColor.transparent)

        lp = QPainter(layer)

        lp.setRenderHint(QPainter.RenderHint.Antialiasing)

        paint(lp)

        lp.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationIn
        )

        fade = QLinearGradient(x0, 0, x0 + w * ramp, 0)

        fade.setColorAt(0.0, QColor(0, 0, 0, 0))

        fade.setColorAt(1.0, QColor(0, 0, 0, 255))

        lp.fillRect(QRectF(0, 0, w, h), fade)

        lp.end()

        p.drawPixmap(0, 0, layer)

    def _render_scene(self, w, h, dpr):

        theme = ThemeManager.get()

        kind = ThemeManager.atmosphere().BANNER

        primary = QColor(theme.Colors.PRIMARY)

        purple = QColor(theme.Colors.PURPLE)

        green = QColor(theme.Colors.GREEN)

        deep = QColor(theme.Colors.BACKGROUND)

        pixmap = QPixmap(round(w * dpr), round(h * dpr))

        pixmap.setDevicePixelRatio(dpr)

        pixmap.fill(Qt.GlobalColor.transparent)

        p = QPainter(pixmap)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        clip = QPainterPath()

        clip.addRoundedRect(
            QRectF(0.5, 0.5, w - 1, h - 1),
            self.glass_radius,
            self.glass_radius
        )

        p.setClipPath(clip)

        # -- base wash

        wash_strength = 0.05 if kind == "wave" else 0.13

        wash = QLinearGradient(0, 0, w, 0)

        c1 = QColor(primary)

        c1.setAlphaF(wash_strength)

        c2 = QColor(primary)

        c2.setAlphaF(wash_strength * 0.35)

        c3 = QColor(purple)

        c3.setAlphaF(wash_strength * 0.9)

        wash.setColorAt(0.0, c1)

        wash.setColorAt(0.45, c2)

        wash.setColorAt(1.0, c3)

        p.fillRect(QRectF(0, 0, w, h), wash)

        x0 = w * 0.36

        if kind == "mountains":

            # horizon glow behind the peaks

            glow = QRadialGradient(QPointF(w * 0.74, h * 0.62), w * 0.30)

            g0 = QColor(primary)

            g0.setAlphaF(0.30)

            g1 = QColor(primary)

            g1.setAlpha(0)

            glow.setColorAt(0.0, g0)

            glow.setColorAt(1.0, g1)

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(glow)

            p.drawEllipse(QPointF(w * 0.74, h * 0.62), w * 0.30, h * 1.0)

            # faint aurora streak across the sky

            streak = QPainterPath()

            streak.moveTo(w * 0.40, h * 0.34)

            streak.cubicTo(
                w * 0.55, h * 0.06,
                w * 0.72, h * 0.52,
                w * 1.02, h * 0.16
            )

            for width, alpha in ((16, 0.05), (9, 0.08), (3, 0.16)):

                tone = QColor(green if width == 3 else primary)

                tone.setAlphaF(alpha)

                p.setBrush(Qt.BrushStyle.NoBrush)

                p.setPen(
                    QPen(tone, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                )

                p.drawPath(streak)

            # a scatter of tiny stars

            rng = random.Random(11)

            p.setPen(Qt.PenStyle.NoPen)

            for _ in range(22):

                sx = rng.uniform(w * 0.42, w * 0.98)

                sy = rng.uniform(h * 0.08, h * 0.50)

                p.setBrush(QColor(255, 255, 255, rng.randint(60, 170)))

                r = rng.uniform(0.5, 1.3)

                p.drawEllipse(QPointF(sx, sy), r, r)

            # far range, near range

            far = QColor(primary)

            far = far.lighter(110)

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(
                self._fade_in_brush(x0, w, far, 0.34)
            )

            p.drawPolygon(
                self._ridge(x0, w, h * 0.74, h * 0.42, 0.9, h)
            )

            near = QColor(deep)

            p.setBrush(
                self._fade_in_brush(x0, w, near, 0.92)
            )

            p.drawPolygon(
                self._ridge(x0, w, h * 0.92, h * 0.36, 3.1, h)
            )

        elif kind == "wave":

            # One thin luminous line - minimal on purpose.

            for offset, alpha, width in ((0.0, 0.85, 1.4), (9.0, 0.22, 1.0)):

                path = QPainterPath()

                steps = 90

                for i in range(steps + 1):

                    fx = i / steps

                    x = w * (0.30 + 0.70 * fx)

                    y = (
                        h * 0.60
                        + offset
                        + math.sin(fx * 8.5 + 0.6) * h * 0.13
                        + math.sin(fx * 21.0) * h * 0.02
                    )

                    if i == 0:

                        path.moveTo(x, y)

                    else:

                        path.lineTo(x, y)

                gradient = QLinearGradient(w * 0.30, 0, w, 0)

                clear = QColor(primary)

                clear.setAlpha(0)

                solid = QColor(primary).lighter(130)

                solid.setAlphaF(alpha)

                gradient.setColorAt(0.0, clear)

                gradient.setColorAt(0.5, solid)

                gradient.setColorAt(1.0, clear)

                p.setBrush(Qt.BrushStyle.NoBrush)

                p.setPen(QPen(gradient, width))

                p.drawPath(path)

        elif kind == "ocean":

            horizon = h * 0.56

            # moon + glow

            moon = QPointF(w * 0.80, h * 0.30)

            halo = QRadialGradient(moon, h * 0.55)

            halo.setColorAt(0.0, QColor(220, 250, 255, 120))

            halo.setColorAt(1.0, QColor(220, 250, 255, 0))

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(halo)

            p.drawEllipse(moon, h * 0.55, h * 0.55)

            p.setBrush(QColor(236, 252, 255, 235))

            p.drawEllipse(moon, 6.5, 6.5)

            # The water lives on its own layer so it can be faded in from
            # the left (DestinationIn) and melt into the quote text.

            layer = QPixmap(round(w * dpr), round(h * dpr))

            layer.setDevicePixelRatio(dpr)

            layer.fill(Qt.GlobalColor.transparent)

            lp = QPainter(layer)

            lp.setRenderHint(QPainter.RenderHint.Antialiasing)

            water = QLinearGradient(0, horizon, 0, h)

            w0 = QColor(primary)

            w0.setAlphaF(0.30)

            w1 = QColor(primary)

            w1.setAlphaF(0.04)

            water.setColorAt(0.0, w0)

            water.setColorAt(1.0, w1)

            lp.fillRect(QRectF(0, horizon, w, h - horizon), water)

            lp.setPen(Qt.PenStyle.NoPen)

            for i in range(6):

                lp.setBrush(QColor(220, 250, 255, max(0, 150 - i * 22)))

                lp.drawEllipse(
                    QPointF(moon.x(), horizon + 6 + i * 7),
                    30 - i * 3.5,
                    1.5
                )

            for base, amp, seed, alpha in (
                (h * 0.68, 2.6, 0.4, 70),
                (h * 0.82, 3.4, 2.2, 45),
            ):

                path = QPainterPath()

                steps = 80

                for i in range(steps + 1):

                    fx = i / steps

                    x = w * fx

                    y = base + math.sin(fx * 30 + seed) * amp

                    if i == 0:

                        path.moveTo(x, y)

                    else:

                        path.lineTo(x, y)

                lp.setBrush(Qt.BrushStyle.NoBrush)

                lp.setPen(QPen(QColor(200, 245, 255, alpha), 1.2))

                lp.drawPath(path)

            lp.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_DestinationIn
            )

            fade = QLinearGradient(x0, 0, x0 + w * 0.30, 0)

            fade.setColorAt(0.0, QColor(0, 0, 0, 0))

            fade.setColorAt(1.0, QColor(0, 0, 0, 255))

            lp.fillRect(QRectF(0, 0, w, h), fade)

            lp.end()

            p.drawPixmap(0, 0, layer)

        elif kind == "orbit":

            # The solar system in a row: sun, then Mercury -> Neptune in
            # order, with the asteroid belt between Mars and Jupiter.

            y = h * 0.56

            sun = QPointF(w * 0.365, y)

            planets = (
                (3.0, (196, 190, 184)),
                (4.6, (246, 222, 164)),
                (5.0, (86, 168, 255)),
                (4.0, (232, 108, 68)),
                (9.5, (226, 178, 128)),
                (8.0, (242, 216, 158)),
                (6.2, (150, 226, 236)),
                (6.0, (78, 118, 255)),
            )

            def paint_orbit(lp):

                lp.setPen(QPen(QColor(255, 236, 210, 44), 1.0))

                lp.drawLine(QPointF(w * 0.365, y), QPointF(w * 0.985, y))

                lp.setPen(Qt.PenStyle.NoPen)

                for i, (radius, color) in enumerate(planets):

                    x = w * 0.42 + (w * 0.555) * (i / 7) ** 0.9

                    halo = QRadialGradient(QPointF(x, y), radius * 3.4)

                    halo.setColorAt(0.0, QColor(*color, 60))

                    halo.setColorAt(1.0, QColor(*color, 0))

                    lp.setBrush(halo)

                    lp.drawEllipse(QPointF(x, y), radius * 3.4, radius * 3.4)

                    body = QRadialGradient(
                        QPointF(x, y),
                        radius,
                        QPointF(x - radius * 0.4, y - radius * 0.4)
                    )

                    base_color = QColor(*color)

                    body.setColorAt(0.0, base_color.lighter(155))

                    body.setColorAt(0.65, base_color)

                    body.setColorAt(1.0, base_color.darker(240))

                    lp.setBrush(body)

                    lp.drawEllipse(QPointF(x, y), radius, radius)

                    if i == 5:

                        lp.setBrush(Qt.BrushStyle.NoBrush)

                        lp.setPen(QPen(QColor(236, 214, 160, 170), 1.5))

                        lp.drawEllipse(QPointF(x, y), radius * 2.0, radius * 0.6)

                        lp.setPen(Qt.PenStyle.NoPen)

                belt_x = w * 0.42 + (w * 0.555) * (3.5 / 7) ** 0.9

                rng = random.Random(5)

                lp.setBrush(QColor(214, 200, 180, 150))

                for _ in range(14):

                    lp.drawEllipse(
                        QPointF(belt_x + rng.uniform(-10, 10), y + rng.uniform(-9, 9)),
                        rng.uniform(0.6, 1.2),
                        rng.uniform(0.6, 1.2)
                    )

            self._faded_layer(p, w, h, dpr, w * 0.40, paint_orbit, ramp=0.10)

            glow = QRadialGradient(sun, h * 0.62)

            glow.setColorAt(0.0, QColor(255, 170, 60, 170))

            glow.setColorAt(1.0, QColor(255, 120, 30, 0))

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(glow)

            p.drawEllipse(sun, h * 0.62, h * 0.62)

            p.setBrush(QColor(255, 236, 170, 255))

            p.drawEllipse(sun, 7.5, 7.5)

        elif kind == "grid":

            horizon = h * 0.56

            center_x = w * 0.72

            def paint_grid(lp):

                halo = QRadialGradient(QPointF(center_x, horizon), h * 0.9)

                halo.setColorAt(0.0, QColor(255, 60, 160, 120))

                halo.setColorAt(1.0, QColor(255, 60, 160, 0))

                lp.setPen(Qt.PenStyle.NoPen)

                lp.setBrush(halo)

                lp.drawEllipse(QPointF(center_x, horizon), h * 0.9, h * 0.9)

                sun_r = h * 0.36

                disc = QPainterPath()

                disc.addEllipse(QPointF(center_x, horizon), sun_r, sun_r)

                above = QPainterPath()

                above.addRect(QRectF(0, 0, w, horizon))

                sun_gradient = QLinearGradient(0, horizon - sun_r, 0, horizon)

                sun_gradient.setColorAt(0.0, QColor(255, 226, 70))

                sun_gradient.setColorAt(0.55, QColor(255, 112, 90))

                sun_gradient.setColorAt(1.0, QColor(255, 36, 150))

                lp.setBrush(sun_gradient)

                lp.drawPath(disc.intersected(above))

                lp.setBrush(QColor(14, 4, 26, 235))

                lp.drawRect(QRectF(0, horizon, w, h - horizon))

                for f in (0.22, 0.45, 0.72, 1.0):

                    yy = horizon + (h - horizon) * f ** 1.6

                    lp.setPen(QPen(QColor(255, 90, 190, 170), 1.0))

                    lp.drawLine(QPointF(0, yy), QPointF(w, yy))

                for i in range(-12, 13):

                    lp.setPen(QPen(QColor(190, 130, 255, 130), 1.0))

                    lp.drawLine(
                        QPointF(center_x + i * w * 0.006, horizon),
                        QPointF(center_x + i * w * 0.06, h)
                    )

                lp.setPen(QPen(QColor(255, 170, 230, 230), 1.4))

                lp.drawLine(QPointF(0, horizon), QPointF(w, horizon))

            self._faded_layer(p, w, h, dpr, x0, paint_grid, ramp=0.22)

        elif kind == "forest":

            moon = QPointF(w * 0.86, h * 0.30)

            halo = QRadialGradient(moon, h * 0.55)

            halo.setColorAt(0.0, QColor(230, 255, 220, 110))

            halo.setColorAt(1.0, QColor(230, 255, 220, 0))

            p.setPen(Qt.PenStyle.NoPen)

            p.setBrush(halo)

            p.drawEllipse(moon, h * 0.55, h * 0.55)

            p.setBrush(QColor(240, 255, 236, 235))

            p.drawEllipse(moon, 6.0, 6.0)

            def paint_trees(lp):

                rng = random.Random(21)

                lp.setPen(Qt.PenStyle.NoPen)

                for row, (color, lo, hi) in enumerate((
                    (QColor(primary).darker(240), 0.30, 0.55),
                    (QColor(deep).darker(150), 0.42, 0.82),
                )):

                    x = x0 - 10

                    while x < w + 10:

                        tree_h = rng.uniform(lo, hi) * h

                        half = tree_h * 0.20

                        top = h + 2 - tree_h

                        color.setAlpha(210 if row == 0 else 250)

                        lp.setBrush(color)

                        for tier in range(3):

                            t0 = top + tier * tree_h * 0.27

                            t1 = top + tree_h * (0.42 + tier * 0.29)

                            spread = half * (0.55 + tier * 0.30)

                            lp.drawPolygon(
                                QPolygonF([
                                    QPointF(x, t0),
                                    QPointF(x - spread, t1),
                                    QPointF(x + spread, t1),
                                ])
                            )

                        x += rng.uniform(13, 22) if row == 1 else rng.uniform(10, 17)

                rng = random.Random(3)

                for _ in range(7):

                    fx = rng.uniform(w * 0.5, w * 0.95)

                    fy = rng.uniform(h * 0.35, h * 0.85)

                    fh = QRadialGradient(QPointF(fx, fy), 9)

                    fh.setColorAt(0.0, QColor(220, 255, 120, 150))

                    fh.setColorAt(1.0, QColor(220, 255, 120, 0))

                    lp.setBrush(fh)

                    lp.drawEllipse(QPointF(fx, fy), 9, 9)

                    lp.setBrush(QColor(255, 255, 200, 230))

                    lp.drawEllipse(QPointF(fx, fy), 1.3, 1.3)

            self._faded_layer(p, w, h, dpr, x0, paint_trees, ramp=0.24)

        elif kind == "snow":

            def paint_hills(lp):

                lp.setPen(Qt.PenStyle.NoPen)

                for base, amp, seed, color in (
                    (h * 0.70, h * 0.10, 0.6, QColor(190, 220, 255, 70)),
                    (h * 0.88, h * 0.09, 2.4, QColor(238, 246, 255, 150)),
                ):

                    points = []

                    steps = 60

                    for i in range(steps + 1):

                        fx = i / steps

                        points.append(
                            QPointF(
                                x0 + (w - x0) * fx,
                                base - amp * (0.5 + 0.5 * math.sin(fx * 5.2 + seed))
                            )
                        )

                    points.append(QPointF(w, h))

                    points.append(QPointF(x0, h))

                    lp.setBrush(color)

                    lp.drawPolygon(QPolygonF(points))

                rng = random.Random(9)

                for _ in range(30):

                    lp.setBrush(QColor(255, 255, 255, rng.randint(90, 220)))

                    r = rng.uniform(0.7, 1.9)

                    lp.drawEllipse(
                        QPointF(rng.uniform(x0, w), rng.uniform(4, h * 0.7)),
                        r,
                        r
                    )

            self._faded_layer(p, w, h, dpr, x0, paint_hills, ramp=0.26)

        p.end()

        return pixmap

    def paintEvent(self, event):

        dpr = self.devicePixelRatioF()

        key = (self.width(), self.height(), dpr, ThemeManager.current_name)

        if self._cache_key != key:

            self._cache = self._render_scene(
                self.width(),
                self.height(),
                dpr
            )

            self._cache_key = key

        painter = QPainter(self)

        painter.drawPixmap(0, 0, self._cache)

        painter.end()

        # QFrame border + the refractive rim, on top of the scene.

        super().paintEvent(event)
