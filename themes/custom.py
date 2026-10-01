"""
Flux - Custom Theme
--------------------
The one theme with no fixed palette: Colors, Style.GLOW/RIM and
Atmosphere.BLOBS/RIBBONS/PARTICLE_COLOR are computed on every access from
whatever the user has picked (themes.custom_state.CustomState), instead
of being constants baked in at import time like every other theme module.

This is done by overriding __getattribute__ on each class's metaclass, so
plain call sites elsewhere in the app - `theme.Colors.PRIMARY`,
`ThemeManager.style().GLOW` - keep working unmodified; they have no idea
this theme is any different from Dark or Ocean.
"""

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)
from themes.custom_state import CustomState
from themes import palette_gen


NAME = "Custom"

ICON = "palette"

DESCRIPTION = "Pick a color, Flux builds the rest of the theme around it."

TAGLINE = "Made by you"


# palette_gen.colors() doesn't have SUCCESS/WARNING/ERROR keys - every
# other theme just repeats GREEN/ORANGE/RED under those three extra
# names, so alias them the same way here.
_COLOR_ALIASES = {"SUCCESS": "GREEN", "WARNING": "ORANGE", "ERROR": "RED"}


class _ColorsMeta(type):

    def __getattribute__(cls, name):

        if name.startswith("_"):

            return type.__getattribute__(cls, name)

        primary, glow = CustomState.get()

        data = palette_gen.colors(primary, glow)

        key = _COLOR_ALIASES.get(name, name)

        if key in data:

            return data[key]

        return type.__getattribute__(cls, name)


class Colors(metaclass=_ColorsMeta):
    pass


class _StyleMeta(type):

    def __getattribute__(cls, name):

        if name == "GLOW":

            return CustomState.get()[1]

        if name == "RIM":

            glow = CustomState.get()[1]

            return max(0.25, min(0.95, 0.3 + glow * 0.65))

        return type.__getattribute__(cls, name)


class Style(metaclass=_StyleMeta):

    CARD_TINT = 0.15

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True


class _AtmosphereMeta(type):

    def __getattribute__(cls, name):

        if name in ("BLOBS", "RIBBONS"):

            primary, glow = CustomState.get()

            blobs, ribbons = palette_gen.atmosphere(primary, glow)

            return blobs if name == "BLOBS" else ribbons

        if name == "PARTICLE_COLOR":

            primary, glow = CustomState.get()

            return palette_gen.colors(primary, glow)["PARTICLE_TINT"]

        return type.__getattribute__(cls, name)


class Atmosphere(metaclass=_AtmosphereMeta):

    KIND = "aurora"

    PARTICLES = "stars"

    PARTICLE_COUNT = 70

    PARTICLE_ALPHA = 0.6

    SHOOTING_STARS = True

    SHOOT_FRAMES = (450, 1200)

    BANNER = "mountains"


def __getattr__(name):

    # PEP 562 module-level dynamic attribute: dark_family_stylesheet(C)
    # reads Colors.* at call time, so building this once at import would
    # freeze in whatever CustomState held that moment. Computing it here
    # means every ThemeManager.stylesheet() call sees the live palette.

    if name == "GLOBAL_STYLESHEET":

        return dark_family_stylesheet(Colors)

    raise AttributeError(name)
