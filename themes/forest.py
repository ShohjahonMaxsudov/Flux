"""
Flux - Forest Theme
A quiet forest at night, drifting fireflies under the moon.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Forest"

ICON = "tree"

DESCRIPTION = "A quiet forest at night, drifting fireflies under the moon."

TAGLINE = "Night woods"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#040C09"
    SECONDARY = "#0C2117"

    SURFACE = "#08150F"
    SURFACE_ALT = "#0E1F17"

    GLASS = "rgba(150,255,190,0.05)"
    GLASS_HOVER = "rgba(150,255,190,0.10)"

    BORDER = "rgba(150,240,190,0.15)"
    BORDER_ACTIVE = "#5FE39B"

    PRIMARY = "#35C78A"
    GREEN = "#A6E34F"
    PURPLE = "#8FA8FF"
    ORANGE = "#F7C948"
    RED = "#FF7A7A"

    TEXT = "#EDFFF5"
    TEXT_SECONDARY = "#88A897"

    SUCCESS = "#A6E34F"
    WARNING = "#F7C948"
    ERROR = "#FF7A7A"


class Style(base.Style):

    CARD_TINT = 0.13

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.55

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.75


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (30, 160, 110, 56, 560, 0.20, 0.90, 0.08, 110, 50),
        (20, 90, 80, 50, 520, 0.80, 0.30, 0.07, 100, 70),
        (220, 255, 200, 16, 420, 0.85, 0.08, 0.05, 50, 40),
    )

    RIBBONS = ()

    PARTICLES = "fireflies"

    PARTICLE_COUNT = 34

    PARTICLE_ALPHA = 0.9

    PARTICLE_COLOR = (220, 255, 120)

    SHOOTING_STARS = False

    SHOOT_FRAMES = (450, 1200)

    BANNER = "forest"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
