"""
Flux - Graphite Mono
Low-distraction monochrome theme for focused work.
"""
from dataclasses import dataclass
from themes import base
from themes.base import dark_family_stylesheet

NAME = "Graphite Mono"
ICON = "contrast"
DESCRIPTION = "Quiet graphite surfaces with restrained silver accents."
TAGLINE = "Less color. More focus."

@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#0B0C0E"
    SECONDARY = "#101215"
    SURFACE = "#15171A"
    SURFACE_ALT = "#1B1E22"
    GLASS = "rgba(235,240,248,0.040)"
    GLASS_HOVER = "rgba(235,240,248,0.080)"
    BORDER = "rgba(225,230,238,0.12)"
    BORDER_ACTIVE = "#B9C0CC"
    PRIMARY = "#CBD2DD"
    GREEN = "#8FD4B7"
    PURPLE = "#B9AFD8"
    ORANGE = "#D8BE8A"
    RED = "#DB9098"
    TEXT = "#F2F3F5"
    TEXT_SECONDARY = "#9298A1"
    SUCCESS = "#8FD4B7"
    WARNING = "#D8BE8A"
    ERROR = "#DB9098"

class Style(base.Style):
    CARD_TINT = 0.08
    ICON_STYLE = "ring"
    PILL_STYLE = "tint"
    NAV_STYLE = "glass"
    GLOW = 0.22
    STAT_ACCENTS = ("PRIMARY", "GREEN", "ORANGE", "PURPLE")
    PANEL_TINT = True
    RIM = 0.48

class Atmosphere(base.Atmosphere):
    KIND = "aurora"
    BLOBS = (
        (160, 170, 190, 20, 540, 0.18, 0.20, 0.07, 90, 60),
        (105, 115, 130, 16, 440, 0.78, 0.82, 0.06, 105, 52),
    )
    RIBBONS = (
        (175, 185, 200, 18, 0.22, 0.04, 0.08, 0.17, 0.86, 0.0, -0.10),
    )
    PARTICLES = "stars"
    PARTICLE_COUNT = 28
    PARTICLE_ALPHA = 0.28
    PARTICLE_COLOR = (225, 230, 238)
    SHOOTING_STARS = False
    BANNER = "mountains"

GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
