"""
Flux — Dark Theme
-----------------
Central design system for the entire application.

Every UI component should import values from here instead of
hardcoding colors, spacing, or fonts.
"""

from dataclasses import dataclass


# ---------------------------------------------------------
# COLORS
# ---------------------------------------------------------

@dataclass(frozen=True)
class Colors:
    BACKGROUND = "#05070D"
    SECONDARY = "#08111F"

    SURFACE = "#0B1323"
    SURFACE_ALT = "#101A2B"

    GLASS = "rgba(255,255,255,0.05)"
    GLASS_HOVER = "rgba(255,255,255,0.08)"

    BORDER = "rgba(255,255,255,0.08)"
    BORDER_ACTIVE = "#5A7DFF"

    PRIMARY = "#5A7DFF"
    GREEN = "#4BE8A5"
    PURPLE = "#A56EFF"
    ORANGE = "#FFC857"
    RED = "#FF6B6B"

    TEXT = "#FFFFFF"
    TEXT_SECONDARY = "#8E9AAF"

    SUCCESS = "#4BE8A5"
    WARNING = "#FFC857"
    ERROR = "#FF6B6B"


# ---------------------------------------------------------
# SPACING
# ---------------------------------------------------------

@dataclass(frozen=True)
class Spacing:
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


# ---------------------------------------------------------
# RADIUS
# ---------------------------------------------------------

@dataclass(frozen=True)
class Radius:
    SMALL = 10
    MEDIUM = 16
    LARGE = 22
    XLARGE = 28


# ---------------------------------------------------------
# FONT
# ---------------------------------------------------------

@dataclass(frozen=True)
class Font:
    FAMILY = "Segoe UI"

    SMALL = 10
    BODY = 11
    SUBTITLE = 13
    TITLE = 18
    HEADER = 28


# ---------------------------------------------------------
# ICON SIZES
# ---------------------------------------------------------

@dataclass(frozen=True)
class Icons:
    SMALL = 16
    MEDIUM = 20
    LARGE = 24
    XLARGE = 32


# ---------------------------------------------------------
# ANIMATION
# ---------------------------------------------------------

@dataclass(frozen=True)
class Animation:
    FAST = 120
    NORMAL = 220
    SLOW = 380

    FPS = 60


# ---------------------------------------------------------
# SHADOWS
# ---------------------------------------------------------

@dataclass(frozen=True)
class Shadow:
    BLUR = 40
    OFFSET = 0
    ALPHA = 70


# ---------------------------------------------------------
# WINDOW
# ---------------------------------------------------------

@dataclass(frozen=True)
class Window:
    MIN_WIDTH = 1200
    MIN_HEIGHT = 760

    START_WIDTH = 1450
    START_HEIGHT = 900


# ---------------------------------------------------------
# GLOBAL STYLESHEET
# ---------------------------------------------------------

GLOBAL_STYLESHEET = f"""
QMainWindow {{
    background: {Colors.BACKGROUND};
}}

QWidget {{
    background: transparent;
    color: {Colors.TEXT};
    font-family: "{Font.FAMILY}";
    font-size: {Font.BODY}pt;
}}

QFrame {{
    background: transparent;
    border: none;
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QScrollBar:vertical {{
    width: 8px;
    background: transparent;
}}

QScrollBar::handle:vertical {{
    background: rgba(255,255,255,0.12);
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(255,255,255,0.22);
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QPushButton {{
    background: transparent;
    border: none;
}}

QLineEdit {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 10px 14px;
    color: white;
}}

QLineEdit:focus {{
    border: 1px solid {Colors.PRIMARY};
}}

QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QToolTip {{
    background: #101827;
    color: white;
    border: 1px solid rgba(255,255,255,0.08);
    padding: 6px;
}}
"""