"""
Flux - Ember Theme
Charcoal dark with a slow glow and rising sparks.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Ember"

ICON = "flame"

DESCRIPTION = "Charcoal dark with a slow glow and rising sparks."

TAGLINE = "Warm sparks"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#0B0504"
    SECONDARY = "#241008"

    SURFACE = "#150A07"
    SURFACE_ALT = "#1E100B"

    GLASS = "rgba(255,160,100,0.055)"
    GLASS_HOVER = "rgba(255,160,100,0.11)"

    BORDER = "rgba(255,170,110,0.16)"
    BORDER_ACTIVE = "#FF8A4C"

    PRIMARY = "#FF6A2E"
    GREEN = "#7ED9A0"
    PURPLE = "#E08CFF"
    ORANGE = "#FFC34D"
    RED = "#FF4D4D"

    TEXT = "#FFF3EA"
    TEXT_SECONDARY = "#B49A8A"

    SUCCESS = "#7ED9A0"
    WARNING = "#FFC34D"
    ERROR = "#FF4D4D"


class Style(base.Style):

    CARD_TINT = 0.14

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.75

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.8


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (255, 100, 40, 60, 560, 0.15, 1.00, 0.08, 120, 40),
        (255, 160, 60, 44, 520, 0.85, 1.05, 0.10, 100, 40),
        (180, 40, 20, 40, 500, 0.50, 0.20, 0.07, 100, 60),
    )

    RIBBONS = (
        (255, 90, 40, 46, 0.88, 0.04, 0.10, 0.20, 0.90, 0.0, 0.03),
    )

    PARTICLES = "embers"

    PARTICLE_COUNT = 55

    PARTICLE_ALPHA = 0.9

    PARTICLE_COLOR = (255, 170, 80)

    SHOOTING_STARS = False

    SHOOT_FRAMES = (450, 1200)

    BANNER = "mountains"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
