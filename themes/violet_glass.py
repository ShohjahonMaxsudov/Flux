"""
Flux - Violet Glass
A richer indigo/violet glass palette for a more expressive workspace.
"""
from dataclasses import dataclass
from themes import base
from themes.base import dark_family_stylesheet

NAME = "Violet Glass"
ICON = "sparkle"
DESCRIPTION = "Smoky charcoal glass with indigo and violet light."
TAGLINE = "Soft neon, no noise."

@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#09080F"
    SECONDARY = "#100D19"
    SURFACE = "#14101F"
    SURFACE_ALT = "#1A1428"
    GLASS = "rgba(180,120,255,0.060)"
    GLASS_HOVER = "rgba(180,120,255,0.120)"
    BORDER = "rgba(190,145,255,0.17)"
    BORDER_ACTIVE = "#A983FF"
    PRIMARY = "#9B7BFF"
    GREEN = "#5BE4B4"
    PURPLE = "#C07CFF"
    ORANGE = "#FFB86B"
    RED = "#FF7189"
    TEXT = "#F8F5FF"
    TEXT_SECONDARY = "#A39AB8"
    SUCCESS = "#5BE4B4"
    WARNING = "#FFB86B"
    ERROR = "#FF7189"

class Style(base.Style):
    CARD_TINT = 0.16
    ICON_STYLE = "ring"
    PILL_STYLE = "tint"
    NAV_STYLE = "glass"
    GLOW = 0.67
    STAT_ACCENTS = ("PRIMARY", "PURPLE", "GREEN", "ORANGE")
    PANEL_TINT = True
    RIM = 0.75

class Atmosphere(base.Atmosphere):
    KIND = "aurora"
    BLOBS = (
        (150, 80, 255, 46, 550, 0.18, 0.18, 0.09, 90, 60),
        (215, 90, 255, 30, 470, 0.78, 0.80, 0.08, 105, 54),
        (80, 110, 255, 24, 420, 0.88, 0.12, 0.10, 82, 70),
    )
    RIBBONS = (
        (155, 85, 255, 40, 0.18, 0.04, 0.10, 0.20, 0.90, 0.0, -0.11),
        (210, 95, 255, 26, 0.35, 0.06, 0.08, 0.15, 0.68, 2.2, -0.15),
    )
    PARTICLES = "stars"
    PARTICLE_COUNT = 52
    PARTICLE_ALPHA = 0.46
    PARTICLE_COLOR = (245, 232, 255)
    SHOOTING_STARS = True
    BANNER = "mountains"

GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
