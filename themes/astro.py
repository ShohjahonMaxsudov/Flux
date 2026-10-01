"""
Flux - Astro Theme
The solar system: a burning sun, all eight planets in order, drifting meteors.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Astro"

ICON = "planet"

DESCRIPTION = "The solar system: a burning sun, all eight planets in order, drifting meteors."

TAGLINE = "Solar system"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#05050E"
    SECONDARY = "#0E0B1F"

    SURFACE = "#0B0A18"
    SURFACE_ALT = "#141026"

    GLASS = "rgba(255,225,190,0.05)"
    GLASS_HOVER = "rgba(255,225,190,0.10)"

    BORDER = "rgba(255,215,170,0.15)"
    BORDER_ACTIVE = "#FFB067"

    PRIMARY = "#FF9A3D"
    GREEN = "#5EE6B0"
    PURPLE = "#A08CFF"
    ORANGE = "#FFD166"
    RED = "#FF6B6B"

    TEXT = "#FFF7EC"
    TEXT_SECONDARY = "#B3A796"

    SUCCESS = "#5EE6B0"
    WARNING = "#FFD166"
    ERROR = "#FF6B6B"


class Style(base.Style):

    CARD_TINT = 0.14

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.7

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.8


class Atmosphere(base.Atmosphere):

    KIND = "astro"

    BLOBS = ()

    RIBBONS = ()

    PARTICLES = "stars"

    PARTICLE_COUNT = 130

    PARTICLE_ALPHA = 0.8

    PARTICLE_COLOR = (255, 244, 225)

    SHOOTING_STARS = True

    SHOOT_FRAMES = (150, 420)

    BANNER = "orbit"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
