from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QPen
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QFrame


def apply_soft_shadow(
    widget,
    blur=36,
    y_offset=12,
    alpha=110
):

    # The native Qt drop shadow — the "floating above the background"
    # depth cue that iOS 26's Liquid Glass pairs with the refractive
    # edge. One shadow effect per widget; Qt owns and cleans it up.

    effect = QGraphicsDropShadowEffect(widget)

    effect.setBlurRadius(blur)

    effect.setOffset(0, y_offset)

    effect.setColor(QColor(0, 0, 0, alpha))

    widget.setGraphicsEffect(effect)


def paint_refractive_border(
    widget,
    radius=18,
    strength=1.0
):

    # The "refractive inner border" from iOS 26's Liquid Glass material:
    # a bright specular stroke traced just inside the shape's edge,
    # brightest along the top where light would catch a curved glass
    # rim, fading to nothing by the time it reaches the bottom. QSS has
    # no equivalent of an inset, direction-aware gradient border, so
    # this is painted by hand on top of the widget's normal (QSS-driven)
    # appearance — call it from the end of a paintEvent, after
    # super().paintEvent(event).

    rect = QRectF(
        widget.rect()
    ).adjusted(0.75, 0.75, -0.75, -0.75)

    if rect.width() <= 0 or rect.height() <= 0:
        return

    path = QPainterPath()

    path.addRoundedRect(
        rect,
        radius,
        radius
    )


    gradient = QLinearGradient(
        rect.topLeft(),
        rect.bottomLeft()
    )

    gradient.setColorAt(
        0.0,
        QColor(255, 255, 255, int(165 * strength))
    )

    gradient.setColorAt(
        0.3,
        QColor(255, 255, 255, int(40 * strength))
    )

    gradient.setColorAt(
        1.0,
        QColor(255, 255, 255, 0)
    )


    painter = QPainter(widget)

    painter.setRenderHint(QPainter.Antialiasing)

    painter.setPen(
        QPen(gradient, 1.5)
    )

    painter.setBrush(Qt.NoBrush)

    painter.drawPath(path)

    painter.end()


class RefractiveGlassMixin:

    # Mix in alongside a QWidget/QFrame subclass to get the refractive
    # inner border drawn automatically after the widget's own paint:
    #
    #     class StatCard(RefractiveGlassMixin, QFrame):
    #         glass_radius = 20
    #
    # glass_radius should match whatever border-radius the widget's own
    # stylesheet uses, so the highlight traces the actual visible edge
    # instead of floating over/inside it.

    glass_radius = 18

    glass_strength = 1.0


    def paintEvent(self, event):

        super().paintEvent(event)

        paint_refractive_border(
            self,
            radius=self.glass_radius,
            strength=self.glass_strength
        )


class GlassFrame(RefractiveGlassMixin, QFrame):

    # Drop-in replacement for a plain QFrame() when a page builds an
    # ad-hoc glass panel inline (page containers, day panels, etc.) and
    # doesn't otherwise need its own subclass. Set .glass_radius on the
    # instance to match whatever border-radius its stylesheet uses.

    glass_radius = 20
