from PySide6.QtGui import QColor


def _hsl_hex(h, s, l):

    c = QColor()

    c.setHslF(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, l)))

    return c.name()


def _hsl_rgba(h, s, l, alpha):

    c = QColor()

    c.setHslF(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, l)))

    return f"rgba({c.red()},{c.green()},{c.blue()},{alpha:g})"


def _hsl_rgb_tuple(h, s, l):

    c = QColor()

    c.setHslF(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, l)))

    return (c.red(), c.green(), c.blue())


def colors(primary_hex, glow):

    # Everything derives from the primary's hue, so any color the user
    # picks produces a coherent palette instead of clashing accents.

    base = QColor(primary_hex)

    if not base.isValid():

        base = QColor("#5A7DFF")

    h, s, l, _ = base.getHslF()

    s = max(s, 0.45)

    primary = base.name()

    purple_h = h + 0.30

    return {

        "BACKGROUND": _hsl_hex(h, min(s, 0.55), 0.045),

        "SECONDARY": _hsl_hex(h, min(s, 0.55), 0.085),

        "SURFACE": _hsl_hex(h, min(s, 0.50), 0.07),

        "SURFACE_ALT": _hsl_hex(h, min(s, 0.50), 0.105),

        "GLASS": _hsl_rgba(h, s, 0.65, 0.055),

        "GLASS_HOVER": _hsl_rgba(h, s, 0.65, 0.11),

        "BORDER": _hsl_rgba(h, s, 0.65, 0.16),

        "BORDER_ACTIVE": _hsl_hex(h, s, 0.68),

        "PRIMARY": primary,

        "GREEN": "#4BE8A5",

        "PURPLE": _hsl_hex(purple_h, min(s + 0.10, 0.85), 0.66),

        "ORANGE": "#FFC857",

        "RED": "#FF6B6B",

        "TEXT": "#F2F5FF",

        "TEXT_SECONDARY": _hsl_hex(h, 0.14, 0.62),

        "PARTICLE_TINT": _hsl_rgb_tuple(h, min(s, 0.20), 0.94),

    }


def atmosphere(primary_hex, glow):

    base = QColor(primary_hex)

    if not base.isValid():

        base = QColor("#5A7DFF")

    r, g, b, _ = base.getRgb()

    h, s, l, _ = base.getHslF()

    purple = _hsl_rgb_tuple(h + 0.30, min(s + 0.10, 0.85), 0.60)

    blob_alpha = int(38 + 34 * glow)

    ribbon_alpha = int(30 + 46 * glow)

    blobs = (

        (r, g, b, blob_alpha, 520, 0.16, 0.20, 0.10, 90, 60),

        (purple[0], purple[1], purple[2], int(blob_alpha * 0.75), 460, 0.85, 0.22, 0.11, 90, 70),

        (r, g, b, int(blob_alpha * 0.55), 500, 0.5, 0.92, 0.07, 120, 50),

    )

    ribbons = (

        (r, g, b, ribbon_alpha, 0.20, 0.05, 0.12, 0.20, 0.9, 0.0, -0.10),

        (purple[0], purple[1], purple[2], int(ribbon_alpha * 0.65), 0.34, 0.06, 0.10, 0.16, 0.7, 2.1, -0.15),

    )

    return blobs, ribbons
