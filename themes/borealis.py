"""
Flux - Borealis Theme
Vivid northern lights over a frozen night sky.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Borealis"

ICON = "aurora"

DESCRIPTION = "Vivid northern lights over a frozen night sky."

TAGLINE = "Northern lights"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#030A0F"
    SECONDARY = "#0A2A24"

    SURFACE = "#08161A"
    SURFACE_ALT = "#0D2126"

    GLASS = "rgba(120,255,200,0.055)"
    GLASS_HOVER = "rgba(120,255,200,0.11)"

    BORDER = "rgba(130,255,210,0.16)"
    BORDER_ACTIVE = "#5CF0B0"

    PRIMARY = "#2FD6A0"
    GREEN = "#7DF0A0"
    PURPLE = "#B08CFF"
    ORANGE = "#FFD27A"
    RED = "#FF7A9A"

    TEXT = "#EAFFF6"
    TEXT_SECONDARY = "#83AA9B"

    SUCCESS = "#7DF0A0"
    WARNING = "#FFD27A"
    ERROR = "#FF7A9A"


class Style(base.Style):

    CARD_TINT = 0.15

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.7

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.8


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (40, 220, 160, 58, 560, 0.20, 0.15, 0.09, 110, 60),
        (120, 90, 255, 44, 520, 0.80, 0.20, 0.10, 100, 70),
        (30, 160, 220, 38, 500, 0.50, 0.95, 0.07, 120, 50),
    )

    RIBBONS = (
        (60, 255, 170, 92, 0.16, 0.07, 0.16, 0.22, 0.90, 0.0, -0.08),
        (110, 255, 210, 60, 0.26, 0.06, 0.12, 0.18, 0.70, 1.7, -0.14),
        (150, 110, 255, 58, 0.36, 0.07, 0.12, 0.15, 0.60, 3.0, -0.06),
        (255, 120, 220, 34, 0.10, 0.05, 0.09, 0.25, 1.10, 4.2, -0.04),
    )

    PARTICLES = "stars"

    PARTICLE_COUNT = 100

    PARTICLE_ALPHA = 0.7

    PARTICLE_COLOR = (230, 255, 245)

    SHOOTING_STARS = True

    SHOOT_FRAMES = (450, 1200)

    BANNER = "mountains"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
