"""
Flux - Snow Theme
Soft falling snow on a cold blue evening.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Snow"

ICON = "snowflake"

DESCRIPTION = "Soft falling snow on a cold blue evening."

TAGLINE = "Winter calm"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#08101C"
    SECONDARY = "#15243D"

    SURFACE = "#0E1828"
    SURFACE_ALT = "#152238"

    GLASS = "rgba(200,225,255,0.06)"
    GLASS_HOVER = "rgba(200,225,255,0.115)"

    BORDER = "rgba(200,225,255,0.17)"
    BORDER_ACTIVE = "#8FC2FF"

    PRIMARY = "#6FAEFF"
    GREEN = "#6EE7C8"
    PURPLE = "#B3A6FF"
    ORANGE = "#FFD08A"
    RED = "#FF8FA3"

    TEXT = "#F3F8FF"
    TEXT_SECONDARY = "#8EA3BF"

    SUCCESS = "#6EE7C8"
    WARNING = "#FFD08A"
    ERROR = "#FF8FA3"


class Style(base.Style):

    CARD_TINT = 0.12

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.5

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.9


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (140, 190, 255, 44, 560, 0.20, 0.20, 0.07, 100, 60),
        (200, 220, 255, 26, 520, 0.85, 0.90, 0.06, 100, 50),
    )

    RIBBONS = ()

    PARTICLES = "snow"

    PARTICLE_COUNT = 90

    PARTICLE_ALPHA = 0.85

    PARTICLE_COLOR = (240, 248, 255)

    SHOOTING_STARS = False

    SHOOT_FRAMES = (450, 1200)

    BANNER = "snow"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
