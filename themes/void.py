"""
Flux - Void Theme
Minimal, clean, futuristic. Less glow, more focus.
"""

from dataclasses import dataclass

from themes import base
from themes.base import (  # noqa: F401
    Spacing, Radius, Font, Icons, Animation, Shadow, Window,
    dark_family_stylesheet,
)


NAME = "Void"

ICON = "void"

DESCRIPTION = "Minimal, clean, futuristic. Less glow, more focus."

TAGLINE = "Minimal focus"


@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#05060A"
    SECONDARY = "#0B0D14"

    SURFACE = "#0A0C12"
    SURFACE_ALT = "#10131B"

    GLASS = "rgba(255,255,255,0.035)"
    GLASS_HOVER = "rgba(255,255,255,0.07)"

    BORDER = "rgba(255,255,255,0.075)"
    BORDER_ACTIVE = "#9BB0FF"

    PRIMARY = "#6F8CFF"
    GREEN = "#5FD8A8"
    PURPLE = "#9F8CF7"
    ORANGE = "#EDBB5E"
    RED = "#F27070"

    TEXT = "#EEF1F8"
    TEXT_SECONDARY = "#7C8598"

    SUCCESS = "#5FD8A8"
    WARNING = "#EDBB5E"
    ERROR = "#F27070"


class Style(base.Style):

    CARD_TINT = 0.0

    ICON_STYLE = "ring"

    PILL_STYLE = "tint"

    NAV_STYLE = "glass"

    GLOW = 0.12

    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")

    PANEL_TINT = False

    RIM = 0.28


class Atmosphere(base.Atmosphere):

    KIND = "aurora"

    BLOBS = (
        (110, 140, 255, 20, 620, 0.14, 0.14, 0.05, 70, 50),
        (255, 255, 255, 6, 700, 0.85, 0.85, 0.04, 90, 60),
    )

    RIBBONS = ()

    PARTICLES = "stars"

    PARTICLE_COUNT = 34

    PARTICLE_ALPHA = 0.34

    PARTICLE_COLOR = (225, 232, 255)

    SHOOTING_STARS = False

    BANNER = "wave"


GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
