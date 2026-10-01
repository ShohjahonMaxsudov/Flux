"""
Flux - Nebula Theme
Deep space feel, soft violet aurora, premium look.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Nebula"

ICON = "sparkle"

DESCRIPTION = "Deep space feel, soft aurora, premium look."

TAGLINE = "Deep space"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#0B0716"
    SECONDARY = "#1A0E33"

    SURFACE = "#140C28"
    SURFACE_ALT = "#1C1138"

    GLASS = "rgba(190,145,255,0.06)"
    GLASS_HOVER = "rgba(190,145,255,0.115)"

    BORDER = "rgba(195,155,255,0.17)"
    BORDER_ACTIVE = "#B48CFF"

    PRIMARY = "#8B6BFF"
    GREEN = "#58E6B4"
    PURPLE = "#D08CFF"
    ORANGE = "#FFB86B"
    RED = "#FF6B9A"

    TEXT = "#F7F2FF"
    TEXT_SECONDARY = "#A99BC9"

    SUCCESS = "#58E6B4"
    WARNING = "#FFB86B"
    ERROR = "#FF6B9A"


class Style(base.Style):

    CARD_TINT = 0.16

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.75

    STAT_ACCENTS = ("PRIMARY", "PURPLE", "GREEN", "ORANGE")

    PANEL_TINT = True

    RIM = 0.8


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (139, 92, 246, 72, 540, 0.20, 0.22, 0.09, 100, 70),
        (217, 70, 239, 42, 460, 0.82, 0.30, 0.11, 90, 80),
        (99, 102, 241, 50, 500, 0.55, 0.95, 0.07, 120, 50),
    )

    RIBBONS = (
        (170, 112, 255, 54, 0.22, 0.05, 0.12, 0.20, 0.85, 0.5, -0.08),
        (236, 120, 240, 32, 0.36, 0.06, 0.09, 0.15, 0.65, 2.4, -0.14),
    )

    PARTICLES = "stars"

    PARTICLE_COUNT = 115

    PARTICLE_ALPHA = 0.72

    PARTICLE_COLOR = (236, 226, 255)

    SHOOTING_STARS = True

    BANNER = "mountains"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
