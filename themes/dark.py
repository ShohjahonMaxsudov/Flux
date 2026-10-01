"""
Flux - Dark Theme  (the "Aurora" look)
--------------------------------------
Deep navy base, translucent glass surfaces with a cool tint, tinted stat
cards, glowing accents, a slow aurora and a sparse starfield. Cleaner
grading and more contrast than the old flat dark.

Every UI component should read its values from here instead of hardcoding
colors, spacing, or fonts.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401  (re-exported design tokens)
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Dark"

ICON = "moon"

DESCRIPTION = "Deep navy with a soft aurora glow and a quiet starfield."

TAGLINE = "Aurora glow"


# ---------------------------------------------------------
# COLORS
# ---------------------------------------------------------

@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#0A0F18"
    SECONDARY = "#111827"

    SURFACE = "#0E1524"
    SURFACE_ALT = "#131B2E"

    GLASS = "rgba(140,165,255,0.055)"
    GLASS_HOVER = "rgba(140,165,255,0.105)"

    BORDER = "rgba(150,175,255,0.15)"
    BORDER_ACTIVE = "#7690FF"

    PRIMARY = "#5A7DFF"
    GREEN = "#4BE8A5"
    PURPLE = "#A56EFF"
    ORANGE = "#FFC857"
    RED = "#FF6B6B"

    TEXT = "#F2F5FF"
    TEXT_SECONDARY = "#8E9BB8"

    SUCCESS = "#4BE8A5"
    WARNING = "#FFC857"
    ERROR = "#FF6B6B"


# ---------------------------------------------------------
# STYLE + ATMOSPHERE
# ---------------------------------------------------------

class Style(base.Style):

    CARD_TINT = 0.15

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.65

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = True

    RIM = 0.7


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (90, 125, 255, 58, 520, 0.16, 0.20, 0.10, 90, 60),
        (40, 205, 190, 32, 480, 0.30, 0.95, 0.08, 110, 50),
        (150, 105, 255, 34, 440, 0.88, 0.12, 0.12, 80, 70),
    )

    RIBBONS = (
        (70, 170, 255, 46, 0.20, 0.05, 0.11, 0.22, 0.90, 0.0, -0.10),
        (60, 235, 200, 30, 0.34, 0.06, 0.09, 0.17, 0.70, 2.1, -0.16),
    )

    PARTICLES = "stars"

    PARTICLE_COUNT = 60

    PARTICLE_ALPHA = 0.5

    PARTICLE_COLOR = (255, 255, 255)

    SHOOTING_STARS = True

    BANNER = "mountains"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
