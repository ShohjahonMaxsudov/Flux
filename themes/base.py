"""
Shared building blocks for every Flux theme.

A theme module provides:

    NAME / ICON / DESCRIPTION   how it is listed in the picker
    Colors                      the palette every widget reads
    Style                       how surfaces are drawn (tint, glow, pills...)
    Atmosphere                  what animates behind the UI
    GLOBAL_STYLESHEET           the app-wide QSS

Style and Atmosphere are optional on old-style themes; ThemeManager falls
back to the defaults below, which reproduce the original look exactly.
"""

from dataclasses import dataclass


# ---------------------------------------------------------
# DESIGN TOKENS (unchanged from the original dark theme)
# ---------------------------------------------------------

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
    FAMILY = "Helvetica"

    SMALL = 10
    BODY = 11
    SUBTITLE = 13
    TITLE = 18
    HEADER = 28


@dataclass(frozen=True)
class Icons:
    SMALL = 16
    MEDIUM = 20
    LARGE = 24
    XLARGE = 32


@dataclass(frozen=True)
class Animation:
    FAST = 120
    NORMAL = 220
    SLOW = 380

    FPS = 60


@dataclass(frozen=True)
class Shadow:
    BLUR = 40
    OFFSET = 0
    ALPHA = 70


@dataclass(frozen=True)
class Window:
    MIN_WIDTH = 1200
    MIN_HEIGHT = 760

    START_WIDTH = 1450
    START_HEIGHT = 900


# ---------------------------------------------------------
# STYLE  (how surfaces are drawn)
# ---------------------------------------------------------

class Style:

    # Defaults == the original flat look (Light / Sakura keep this).

    # 0..0.3 - alpha of the accent gradient washed over stat cards.
    CARD_TINT = 0.0

    # "solid": filled accent circle.  "ring": tinted disc + glowing ring.
    ICON_STYLE = "solid"

    # "solid": filled priority/category pills.  "tint": translucent pills.
    PILL_STYLE = "solid"

    # "solid": filled active nav item.  "glass": tinted glass with a rim.
    NAV_STYLE = "solid"

    # 0..1 - strength of coloured glow around primary buttons / rings.
    GLOW = 0.0

    # Names of Colors attributes used for the four stat cards, in order.
    # None -> every card uses PRIMARY (original behaviour).
    STAT_ACCENTS = None

    # True -> soft accent gradient on side panels / progress card.
    PANEL_TINT = False

    # 0..1 - strength of the bright refractive rim traced along the top
    # edge of every glass surface (Void turns it way down).
    RIM = 1.0


# ---------------------------------------------------------
# ATMOSPHERE  (what moves behind the UI)
# ---------------------------------------------------------

class Atmosphere:

    # "aurora": AuroraBackground + particles.  "sakura": petals.
    # "astro": solar system.  "synthwave": neon sunset + grid.  "none".
    KIND = "aurora"

    # Soft drifting colour clouds:
    # (r, g, b, alpha, radius, orbit_x, orbit_y, speed, amp_x, amp_y)
    BLOBS = ()

    # Flowing aurora ribbons:
    # (r, g, b, alpha, y, amplitude, thickness, speed, wavelength, phase, tilt)
    # y / amplitude / thickness / tilt are fractions of the window height,
    # wavelength is a fraction of the width.
    RIBBONS = ()

    # "stars" | "bubbles" | "embers" | "snow" | "fireflies" | "none"
    PARTICLES = "stars"

    PARTICLE_COUNT = 70

    # 0..1 multiplier on particle brightness
    PARTICLE_ALPHA = 0.6

    PARTICLE_COLOR = (255, 255, 255)

    SHOOTING_STARS = True

    # (min, max) frames between shooting stars, at ~30 frames per second.
    SHOOT_FRAMES = (450, 1200)

    # Decorative strip on the dashboard:
    # "mountains" | "wave" | "ocean" | "orbit" | "grid" | "forest" | "snow" | "plain"
    BANNER = "plain"


# ---------------------------------------------------------
# GLOBAL STYLESHEET for the dark-family themes
# ---------------------------------------------------------

def dark_family_stylesheet(C, font_family=Font.FAMILY, body_pt=Font.BODY):

    return f"""
QMainWindow {{
    background: {C.BACKGROUND};
}}

QWidget {{
    background: transparent;
    color: {C.TEXT};
    font-family: "{font_family}";
    font-size: {body_pt}pt;
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
    background: {C.GLASS};
    border: 1px solid {C.BORDER};
    border-radius: 12px;
    padding: 10px 14px;
    color: {C.TEXT};
}}

QLineEdit:focus {{
    border: 1px solid {C.PRIMARY};
}}

QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QToolTip {{
    background: {C.SURFACE_ALT};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    padding: 6px;
}}
"""
