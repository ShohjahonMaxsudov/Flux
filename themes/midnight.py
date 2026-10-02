"""Flux v3 visual identity — one deliberate dark-blue system, not a recolor theme."""

from dataclasses import dataclass
from themes import base
from themes.base import dark_family_stylesheet

NAME = "Flux Midnight"
ICON = "moon"
DESCRIPTION = "Flux's permanent visual identity."
TAGLINE = "Built for focus."


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#080D14"
    SECONDARY = "#0B121C"
    SURFACE = "#0E1621"
    SURFACE_ALT = "#121C29"
    SURFACE_RAISED = "#162231"

    GLASS = "rgba(32,48,70,0.62)"
    GLASS_HOVER = "rgba(46,65,92,0.72)"

    BORDER = "rgba(130,155,190,0.15)"
    BORDER_ACTIVE = "#6A91FF"

    PRIMARY = "#4F67F4"
    PRIMARY_LIGHT = "#6D93FF"
    BLUE_SOFT = "#73A8FF"
    GREEN = "#5BD69A"
    PURPLE = "#9A72F8"
    ORANGE = "#FF894F"
    YELLOW = "#F1C55E"
    RED = "#FF6B7D"

    TEXT = "#F4F7FC"
    TEXT_SECONDARY = "#8F9DB1"
    TEXT_TERTIARY = "#657389"

    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED


class Style(base.Style):
    CARD_TINT = 0.10
    ICON_STYLE = "ring"
    PILL_STYLE = "tint"
    NAV_STYLE = "solid"
    GLOW = 0.22
    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")
    PANEL_TINT = True
    RIM = 0.46


class Atmosphere(base.Atmosphere):
    KIND = "none"
    BLOBS = ()
    RIBBONS = ()
    PARTICLES = "none"
    PARTICLE_COUNT = 0
    PARTICLE_ALPHA = 0.0
    SHOOTING_STARS = False
    BANNER = "none"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
