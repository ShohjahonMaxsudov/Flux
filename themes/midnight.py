"""
Flux - Midnight Blue
Premium default: deep ink surfaces with restrained electric-blue highlights.
"""
from dataclasses import dataclass
from themes import base
from themes.base import dark_family_stylesheet

NAME = "Midnight Blue"
ICON = "moon"
DESCRIPTION = "Deep midnight glass with crisp blue and cyan highlights."
TAGLINE = "Calm. Sharp. Focused."

@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#070B12"
    SECONDARY = "#0B1220"
    SURFACE = "#0D1523"
    SURFACE_ALT = "#121D2E"
    GLASS = "rgba(95,150,255,0.060)"
    GLASS_HOVER = "rgba(95,150,255,0.115)"
    BORDER = "rgba(115,165,255,0.16)"
    BORDER_ACTIVE = "#6EA8FF"
    PRIMARY = "#5D9BFF"
    GREEN = "#47E0B1"
    PURPLE = "#8E7CFF"
    ORANGE = "#FFBE63"
    RED = "#FF6D7A"
    TEXT = "#F5F8FF"
    TEXT_SECONDARY = "#8C9AB3"
    SUCCESS = "#47E0B1"
    WARNING = "#FFBE63"
    ERROR = "#FF6D7A"

class Style(base.Style):
    CARD_TINT = 0.13
    ICON_STYLE = "ring"
    PILL_STYLE = "tint"
    NAV_STYLE = "glass"
    GLOW = 0.55
    STAT_ACCENTS = ("PRIMARY", "GREEN", "PURPLE", "ORANGE")
    PANEL_TINT = True
    RIM = 0.72

class Atmosphere(base.Atmosphere):
    KIND = "aurora"
    BLOBS = (
        (55, 125, 255, 48, 560, 0.14, 0.18, 0.08, 95, 58),
        (35, 205, 220, 26, 470, 0.78, 0.88, 0.07, 105, 52),
        (125, 105, 255, 26, 430, 0.90, 0.12, 0.10, 78, 68),
    )
    RIBBONS = (
        (60, 145, 255, 38, 0.18, 0.04, 0.09, 0.20, 0.92, 0.1, -0.10),
        (35, 220, 215, 24, 0.36, 0.05, 0.08, 0.15, 0.66, 2.0, -0.14),
    )
    PARTICLES = "stars"
    PARTICLE_COUNT = 48
    PARTICLE_ALPHA = 0.42
    PARTICLE_COLOR = (220, 235, 255)
    SHOOTING_STARS = True
    BANNER = "mountains"

GLOBAL_STYLESHEET = dark_family_stylesheet(Colors)
