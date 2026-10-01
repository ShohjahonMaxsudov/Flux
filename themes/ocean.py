"""
Flux - Ocean Theme
Cooler tones, calm and relaxing.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Ocean"

ICON = "wave"

DESCRIPTION = "Cooler tones, calm and relaxing."

TAGLINE = "Calm and cool"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#03111A"
    SECONDARY = "#0A2C3A"

    SURFACE = "#0A1E2A"
    SURFACE_ALT = "#0F2A39"

    GLASS = "rgba(120,225,255,0.06)"
    GLASS_HOVER = "rgba(120,225,255,0.115)"

    BORDER = "rgba(130,230,255,0.16)"
    BORDER_ACTIVE = "#3FD8F5"

    PRIMARY = "#1FB4EC"
    GREEN = "#3FE8B2"
    PURPLE = "#7F9CFF"
    ORANGE = "#FFC56B"
    RED = "#FF7B8B"

    TEXT = "#EAFBFF"
    TEXT_SECONDARY = "#86ABBB"

    SUCCESS = "#3FE8B2"
    WARNING = "#FFC56B"
    ERROR = "#FF7B8B"


class Style(base.Style):

    CARD_TINT = 0.15

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.6

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.8


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (20, 184, 166, 62, 540, 0.18, 0.90, 0.08, 120, 50),
        (34, 211, 238, 44, 500, 0.75, 0.20, 0.10, 100, 80),
        (37, 99, 235, 56, 520, 0.45, 0.55, 0.06, 140, 90),
    )

    RIBBONS = (
        (80, 220, 255, 42, 0.16, 0.045, 0.13, 0.16, 1.00, 1.2, -0.05),
        (60, 240, 200, 28, 0.30, 0.050, 0.10, 0.13, 0.75, 3.4, -0.10),
    )

    PARTICLES = "bubbles"

    PARTICLE_COUNT = 26

    PARTICLE_ALPHA = 0.55

    PARTICLE_COLOR = (170, 240, 255)

    SHOOTING_STARS = False

    BANNER = "ocean"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
