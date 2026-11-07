"""The Custom theme: pick one colour and Flux builds the whole theme around it.

Nothing here is fixed. The palette, glow and animated background are worked out
from the user's colour every time they are read, so moving the colour / glow
controls in Settings updates the whole app live.
"""

from types import SimpleNamespace

from PySide6.QtGui import QColor

from themes.catalog import GLASS, Theme
from themes.qss import dark_qss
from utils.settings_manager import SettingsManager

DEFAULT_PRIMARY = "#5A7DFF"


class CustomState:
    # The Custom theme's two knobs, saved in the settings table. They are
    # loaded lazily (the first time anything asks) rather than at import, so
    # importing this module doesn't open a database connection.
    primary = DEFAULT_PRIMARY
    glow = 0.65
    _loaded = False

    @classmethod
    def _ensure_loaded(cls):
        if cls._loaded:
            return

        cls._loaded = True
        manager = SettingsManager()
        cls.primary = manager.get("custom_theme_primary", cls.primary) or cls.primary

        try:
            cls.glow = float(manager.get("custom_theme_glow", str(cls.glow)))
        except (TypeError, ValueError):
            pass

        manager.close()

    @classmethod
    def get(cls):
        cls._ensure_loaded()
        return cls.primary, cls.glow

    @classmethod
    def set(cls, primary=None, glow=None):
        cls._ensure_loaded()

        if primary is not None:
            cls.primary = primary

        if glow is not None:
            cls.glow = max(0.0, min(1.0, glow))

        manager = SettingsManager()
        manager.set("custom_theme_primary", cls.primary)
        manager.set("custom_theme_glow", str(cls.glow))
        manager.close()


# ---------------------------------------------------------
# Palette generation - everything derives from the primary's hue, so any
# colour the user picks produces a coherent palette instead of clashing accents.
# ---------------------------------------------------------

def _hsl(h, s, l):
    c = QColor()
    c.setHslF(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, l)))
    return c


def _hsl_hex(h, s, l):
    return _hsl(h, s, l).name()


def _hsl_rgba(h, s, l, alpha):
    c = _hsl(h, s, l)
    return f"rgba({c.red()},{c.green()},{c.blue()},{alpha:g})"


def _hsl_rgb(h, s, l):
    c = _hsl(h, s, l)
    return (c.red(), c.green(), c.blue())


def _base_color(primary_hex):
    base = QColor(primary_hex)
    return base if base.isValid() else QColor(DEFAULT_PRIMARY)


def _palette(primary_hex):
    base = _base_color(primary_hex)
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
        "PARTICLE_TINT": _hsl_rgb(h, min(s, 0.20), 0.94),
    }


def _scene(primary_hex, glow):
    """-> (blobs, ribbons) for the animated background"""

    base = _base_color(primary_hex)
    r, g, b, _ = base.getRgb()
    h, s, l, _ = base.getHslF()
    purple = _hsl_rgb(h + 0.30, min(s + 0.10, 0.85), 0.60)
    blob_alpha = int(38 + 34 * glow)
    ribbon_alpha = int(30 + 46 * glow)

    blobs = (
        (r, g, b, blob_alpha, 520, 0.16, 0.20, 0.10, 90, 60),
        (*purple, int(blob_alpha * 0.75), 460, 0.85, 0.22, 0.11, 90, 70),
        (r, g, b, int(blob_alpha * 0.55), 500, 0.5, 0.92, 0.07, 120, 50),
    )

    ribbons = (
        (r, g, b, ribbon_alpha, 0.20, 0.05, 0.12, 0.20, 0.9, 0.0, -0.10),
        (*purple, int(ribbon_alpha * 0.65), 0.34, 0.06, 0.10, 0.16, 0.7, 2.1, -0.15),
    )

    return blobs, ribbons


# ---------------------------------------------------------
# The theme object. Same shape as the built-in ones (see catalog.Theme), but
# these three parts are computed from CustomState whenever they are read.
# ---------------------------------------------------------

class _CustomColors:
    def __getattr__(self, name):
        if not name.startswith("_"):
            palette = _palette(CustomState.get()[0])

            if name in palette:
                return palette[name]

        raise AttributeError(name)


class _CustomStyle(SimpleNamespace):
    @property
    def GLOW(self):
        return CustomState.get()[1]

    @property
    def RIM(self):
        # The glass rim gets brighter as the glow goes up.
        return max(0.25, min(0.95, 0.3 + CustomState.get()[1] * 0.65))


class _CustomAtmosphere(SimpleNamespace):
    @property
    def BLOBS(self):
        return _scene(*CustomState.get())[0]

    @property
    def RIBBONS(self):
        return _scene(*CustomState.get())[1]

    @property
    def PARTICLE_COLOR(self):
        return _palette(CustomState.get()[0])["PARTICLE_TINT"]


CUSTOM = Theme(
    name="Custom",
    icon="palette",
    tagline="Made by you",
    description="Pick a color, Flux builds the rest of the theme around it.",
    colors=_CustomColors(),
    style=_CustomStyle(**GLASS, CARD_TINT=0.15),
    atmosphere=_CustomAtmosphere(
        KIND="aurora",
        PARTICLES="stars",
        PARTICLE_COUNT=70,
        PARTICLE_ALPHA=0.6,
        SHOOTING_STARS=True,
        SHOOT_FRAMES=(450, 1200),
        BANNER="mountains",
    ),
    qss=dark_qss,
)
