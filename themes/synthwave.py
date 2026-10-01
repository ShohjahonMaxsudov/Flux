"""
Flux - Synthwave Theme
Retro neon: a striped sunset over a glowing grid.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Synthwave"

ICON = "sunset"

DESCRIPTION = "Retro neon: a striped sunset over a glowing grid."

TAGLINE = "Neon sunset"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#0E0518"
    SECONDARY = "#2A0B45"

    SURFACE = "#160A26"
    SURFACE_ALT = "#1E0F36"

    GLASS = "rgba(255,120,220,0.06)"
    GLASS_HOVER = "rgba(255,120,220,0.12)"

    BORDER = "rgba(255,120,230,0.20)"
    BORDER_ACTIVE = "#FF5CC0"

    PRIMARY = "#FF2E97"
    GREEN = "#2DE2E6"
    PURPLE = "#B266FF"
    ORANGE = "#FFB800"
    RED = "#FF4D6D"

    TEXT = "#FFF0FA"
    TEXT_SECONDARY = "#BE9AD6"

    SUCCESS = "#2DE2E6"
    WARNING = "#FFB800"
    ERROR = "#FF4D6D"


class Style(base.Style):

    CARD_TINT = 0.15

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.85

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.9


class Atmosphere(base.Atmosphere):

    KIND = "synthwave"

    BLOBS = ()

    RIBBONS = ()

    PARTICLES = "stars"

    PARTICLE_COUNT = 60

    PARTICLE_ALPHA = 0.6

    PARTICLE_COLOR = (255, 225, 250)

    SHOOTING_STARS = False

    SHOOT_FRAMES = (450, 1200)

    BANNER = "grid"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
