"""
Flux — Sakura Theme
Dark, moody cherry-blossom glass — deep plum/maroon base with vivid
pink accents, not a pastel light theme. Matches the reference: dark
translucent cards over an atmospheric blossom photo, white text,
saturated pink icon badges and buttons.
"""

from dataclasses import dataclass



@dataclass(frozen=True)
class Colors:


    BACKGROUND = "#2B1826"

    SECONDARY = "#3D2136"


    SURFACE = "#3A2233"

    SURFACE_ALT = "#452A3F"


    GLASS = "rgba(255,255,255,0.07)"

    GLASS_HOVER = "rgba(255,255,255,0.12)"


    BORDER = "rgba(255,255,255,0.12)"

    BORDER_ACTIVE = "#FF6FA5"



    PRIMARY = "#FF4D94"

    GREEN = "#6FCF97"

    PURPLE = "#8B7FE8"

    ORANGE = "#FFAE5C"

    RED = "#FF6B81"



    TEXT = "#FDF3F8"

    TEXT_SECONDARY = "#CBA3B8"



@dataclass(frozen=True)
class Spacing:

    XS=4
    SM=8
    MD=16
    LG=24
    XL=32
    XXL=48



@dataclass(frozen=True)
class Radius:

    SMALL=10
    MEDIUM=16
    LARGE=22
    XLARGE=28



@dataclass(frozen=True)
class Font:

    FAMILY="Segoe UI"

    SMALL=10
    BODY=11
    SUBTITLE=13
    TITLE=18
    HEADER=28



GLOBAL_STYLESHEET=f"""

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


QLineEdit {{

background:{Colors.SURFACE_ALT};

border:
1px solid {Colors.BORDER};

border-radius:14px;

padding:10px;

color:{Colors.TEXT};

}}


QScrollBar::handle:vertical {{

background:{Colors.PRIMARY};

border-radius:4px;

}}

"""



# ---------------------------------------------------------
# PICKER METADATA / STYLE / ATMOSPHERE
# ---------------------------------------------------------

from themes import base


NAME = "Sakura"

ICON = "blossom"

DESCRIPTION = "Cherry blossom dusk, deep plum and pink."

TAGLINE = "Blossom dusk"


class Style(base.Style):

    pass


class Atmosphere(base.Atmosphere):

    KIND = "sakura"

    BANNER = "mountains"
