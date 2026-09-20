"""
Flux — Light Theme
Clean Apple/Notion inspired light mode.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Colors:

    BACKGROUND = "#F6F7FB"
    SECONDARY = "#EEF1F7"

    SURFACE = "#FFFFFF"
    SURFACE_ALT = "#F0F2F8"

    GLASS = "rgba(0,0,0,0.04)"
    GLASS_HOVER = "rgba(0,0,0,0.08)"

    BORDER = "rgba(0,0,0,0.08)"
    BORDER_ACTIVE = "#4C6FFF"

    PRIMARY = "#4C6FFF"

    GREEN = "#34C759"
    PURPLE = "#AF52DE"
    ORANGE = "#FF9500"
    RED = "#FF3B30"

    TEXT = "#111318"
    TEXT_SECONDARY = "#687086"


@dataclass(frozen=True)
class Spacing:

    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


@dataclass(frozen=True)
class Radius:

    SMALL = 10
    MEDIUM = 16
    LARGE = 22
    XLARGE = 28


@dataclass(frozen=True)
class Font:

    FAMILY = "Segoe UI"

    SMALL = 10
    BODY = 11
    SUBTITLE = 13
    TITLE = 18
    HEADER = 28



GLOBAL_STYLESHEET = f"""

QMainWindow {{
    background:{Colors.BACKGROUND};
}}


QWidget {{
    background:transparent;
    color:{Colors.TEXT};
    font-family:"{Font.FAMILY}";
}}


QFrame {{
    border:none;
}}


QPushButton {{
    background:transparent;
    border:none;
}}


QLineEdit {{
    background:{Colors.SURFACE};
    border:1px solid {Colors.BORDER};
    border-radius:12px;
    padding:10px 14px;
    color:{Colors.TEXT};
}}


QScrollBar:vertical {{
    width:8px;
    background:transparent;
}}


QScrollBar::handle:vertical {{
    background:rgba(0,0,0,0.15);
    border-radius:4px;
}}

"""