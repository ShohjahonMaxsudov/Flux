"""
Flux - Mono Theme
Strictly monochrome. No colour, no distraction.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Mono"

ICON = "contrast"

DESCRIPTION = "Strictly monochrome. No colour, no distraction."

TAGLINE = "Pure black and white"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#060606"
    SECONDARY = "#141414"

    SURFACE = "#0D0D0D"
    SURFACE_ALT = "#171717"

    GLASS = "rgba(255,255,255,0.04)"
    GLASS_HOVER = "rgba(255,255,255,0.08)"

    BORDER = "rgba(255,255,255,0.10)"
    BORDER_ACTIVE = "#CFCFCF"

    PRIMARY = "#8A8A8A"
    GREEN = "#7C7C7C"
    PURPLE = "#A5A5A5"
    ORANGE = "#B8B8B8"
    RED = "#F2F2F2"

    TEXT = "#F0F0F0"
    TEXT_SECONDARY = "#828282"

    SUCCESS = "#7C7C7C"
    WARNING = "#B8B8B8"
    ERROR = "#F2F2F2"


class Style(base.Style):

    CARD_TINT = 0.08

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.0

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = False

    RIM = 0.35


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (255, 255, 255, 10, 600, 0.15, 0.15, 0.05, 80, 50),
    )

    RIBBONS = ()

    PARTICLES = "stars"

    PARTICLE_COUNT = 40

    PARTICLE_ALPHA = 0.4

    PARTICLE_COLOR = (255, 255, 255)

    SHOOTING_STARS = False

    SHOOT_FRAMES = (450, 1200)

    BANNER = "wave"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
