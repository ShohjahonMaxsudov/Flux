"""Every built-in theme, as plain data.

To change a theme, edit its entry in THEMES. To add a new one, copy an entry,
give it a new key, and it shows up in the theme picker automatically.

Each entry has:
    name / icon / tagline / description   how it is listed in the picker
    colors       the palette every widget reads
    style        how surfaces are drawn (glow, tinted cards, pills...)
    atmosphere   what animates behind the UI

Anything a theme leaves out of style / atmosphere falls back to the defaults below.
"""

from types import SimpleNamespace

from themes.qss import dark_qss, light_qss, sakura_qss

STYLE_DEFAULTS = dict(
    # 0..0.3 - alpha of the accent gradient washed over stat cards.
    CARD_TINT=0.0,
    # "solid": filled accent circle.  "ring": tinted disc + glowing ring.
    ICON_STYLE="solid",
    # "solid": filled priority/category pills.  "tint": translucent pills.
    PILL_STYLE="solid",
    # "solid": filled active nav item.  "glass": tinted glass with a rim.
    NAV_STYLE="solid",
    # 0..1 - strength of the coloured glow around primary buttons / rings.
    GLOW=0.0,
    # Colors names used for the four stat cards, in order. None -> all use PRIMARY.
    STAT_ACCENTS=None,
    # True -> soft accent gradient on side panels / progress card.
    PANEL_TINT=False,
    # 0..1 - strength of the bright rim traced along the top edge of glass surfaces.
    RIM=1.0,
)

ATMOSPHERE_DEFAULTS = dict(
    # "aurora": colour clouds + ribbons + particles.  "sakura": petals.
    # "astro": solar system.  "synthwave": neon sunset + grid.  "none": calm flat surface.
    KIND="aurora",
    # Soft drifting colour clouds:
    # (r, g, b, alpha, radius, orbit_x, orbit_y, speed, amp_x, amp_y)
    BLOBS=(),
    # Flowing aurora ribbons:
    # (r, g, b, alpha, y, amplitude, thickness, speed, wavelength, phase, tilt)
    # y / amplitude / thickness / tilt are fractions of the window height,
    # wavelength is a fraction of the width.
    RIBBONS=(),
    # "stars" | "bubbles" | "embers" | "snow" | "fireflies" | "none"
    PARTICLES="stars",
    PARTICLE_COUNT=70,
    # 0..1 multiplier on particle brightness.
    PARTICLE_ALPHA=0.6,
    PARTICLE_COLOR=(255, 255, 255),
    SHOOTING_STARS=True,
    # (min, max) frames between shooting stars, at ~30 frames per second.
    SHOOT_FRAMES=(450, 1200),
    # Decorative strip on the dashboard:
    # "mountains" | "wave" | "ocean" | "orbit" | "grid" | "forest" | "snow" | "plain"
    BANNER="plain",
)

# The look shared by every dark theme; each one only adds its own glow/tint numbers.
GLASS = dict(
    ICON_STYLE="ring",
    PILL_STYLE="tint",
    NAV_STYLE="glass",
    PANEL_TINT=True,
    STAT_ACCENTS=("PRIMARY", "GREEN", "ORANGE", "PURPLE"),
)


class Theme:
    """What the rest of the app reads: theme.Colors, theme.Style, theme.Atmosphere, ..."""

    def __init__(self, name, icon, tagline, description, colors, style, atmosphere, qss):
        self.NAME = name
        self.ICON = icon
        self.TAGLINE = tagline
        self.DESCRIPTION = description
        self.Colors = colors
        self.Style = style
        self.Atmosphere = atmosphere
        self._qss = qss

    @property
    def GLOBAL_STYLESHEET(self):
        # Built on demand, so the Custom theme always reflects its current colours.
        return self._qss(self.Colors)


def theme(name, icon, tagline, description, colors, style=None, atmosphere=None, qss=dark_qss):
    """Build a Theme from plain dicts, filling in the style / atmosphere defaults."""

    return Theme(
        name,
        icon,
        tagline,
        description,
        SimpleNamespace(**colors),
        SimpleNamespace(**{**STYLE_DEFAULTS, **(style or {})}),
        SimpleNamespace(**{**ATMOSPHERE_DEFAULTS, **(atmosphere or {})}),
        qss,
    )


THEMES = {
    "dark": theme(
        name="Dark",
        icon="moon",
        tagline="Aurora glow",
        description="Deep navy with a soft aurora glow and a quiet starfield.",
        colors=dict(
            BACKGROUND="#0A0F18",
            SECONDARY="#111827",
            SURFACE="#0E1524",
            SURFACE_ALT="#131B2E",
            GLASS="rgba(140,165,255,0.055)",
            GLASS_HOVER="rgba(140,165,255,0.105)",
            BORDER="rgba(150,175,255,0.15)",
            BORDER_ACTIVE="#7690FF",
            PRIMARY="#5A7DFF",
            GREEN="#4BE8A5",
            PURPLE="#A56EFF",
            ORANGE="#FFC857",
            RED="#FF6B6B",
            TEXT="#F2F5FF",
            TEXT_SECONDARY="#8E9BB8",
        ),
        style=dict(GLASS, CARD_TINT=0.15, GLOW=0.65, RIM=0.7),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (90, 125, 255, 58, 520, 0.16, 0.20, 0.10, 90, 60),
                (40, 205, 190, 32, 480, 0.30, 0.95, 0.08, 110, 50),
                (150, 105, 255, 34, 440, 0.88, 0.12, 0.12, 80, 70),
            ),
            RIBBONS=(
                (70, 170, 255, 46, 0.20, 0.05, 0.11, 0.22, 0.90, 0.0, -0.10),
                (60, 235, 200, 30, 0.34, 0.06, 0.09, 0.17, 0.70, 2.1, -0.16),
            ),
            PARTICLE_COUNT=60,
            PARTICLE_ALPHA=0.5,
            BANNER="mountains",
        ),
    ),
    "nebula": theme(
        name="Nebula",
        icon="sparkle",
        tagline="Deep space",
        description="Deep space feel, soft aurora, premium look.",
        colors=dict(
            BACKGROUND="#0B0716",
            SECONDARY="#1A0E33",
            SURFACE="#140C28",
            SURFACE_ALT="#1C1138",
            GLASS="rgba(190,145,255,0.06)",
            GLASS_HOVER="rgba(190,145,255,0.115)",
            BORDER="rgba(195,155,255,0.17)",
            BORDER_ACTIVE="#B48CFF",
            PRIMARY="#8B6BFF",
            GREEN="#58E6B4",
            PURPLE="#D08CFF",
            ORANGE="#FFB86B",
            RED="#FF6B9A",
            TEXT="#F7F2FF",
            TEXT_SECONDARY="#A99BC9",
        ),
        style=dict(
            GLASS,
            CARD_TINT=0.16,
            GLOW=0.75,
            RIM=0.8,
            STAT_ACCENTS=("PRIMARY", "PURPLE", "GREEN", "ORANGE"),
        ),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (139, 92, 246, 72, 540, 0.20, 0.22, 0.09, 100, 70),
                (217, 70, 239, 42, 460, 0.82, 0.30, 0.11, 90, 80),
                (99, 102, 241, 50, 500, 0.55, 0.95, 0.07, 120, 50),
            ),
            RIBBONS=(
                (170, 112, 255, 54, 0.22, 0.05, 0.12, 0.20, 0.85, 0.5, -0.08),
                (236, 120, 240, 32, 0.36, 0.06, 0.09, 0.15, 0.65, 2.4, -0.14),
            ),
            PARTICLE_COUNT=115,
            PARTICLE_ALPHA=0.72,
            PARTICLE_COLOR=(236, 226, 255),
            BANNER="mountains",
        ),
    ),
    "void": theme(
        name="Void",
        icon="void",
        tagline="Minimal focus",
        description="Minimal, clean, futuristic. Less glow, more focus.",
        colors=dict(
            BACKGROUND="#05060A",
            SECONDARY="#0B0D14",
            SURFACE="#0A0C12",
            SURFACE_ALT="#10131B",
            GLASS="rgba(255,255,255,0.035)",
            GLASS_HOVER="rgba(255,255,255,0.07)",
            BORDER="rgba(255,255,255,0.075)",
            BORDER_ACTIVE="#9BB0FF",
            PRIMARY="#6F8CFF",
            GREEN="#5FD8A8",
            PURPLE="#9F8CF7",
            ORANGE="#EDBB5E",
            RED="#F27070",
            TEXT="#EEF1F8",
            TEXT_SECONDARY="#7C8598",
        ),
        style=dict(GLASS, CARD_TINT=0.0, GLOW=0.12, RIM=0.28, PANEL_TINT=False),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (110, 140, 255, 20, 620, 0.14, 0.14, 0.05, 70, 50),
                (255, 255, 255, 6, 700, 0.85, 0.85, 0.04, 90, 60),
            ),
            PARTICLE_COUNT=34,
            PARTICLE_ALPHA=0.34,
            PARTICLE_COLOR=(225, 232, 255),
            SHOOTING_STARS=False,
            BANNER="wave",
        ),
    ),
    "ocean": theme(
        name="Ocean",
        icon="wave",
        tagline="Calm and cool",
        description="Cooler tones, calm and relaxing.",
        colors=dict(
            BACKGROUND="#03111A",
            SECONDARY="#0A2C3A",
            SURFACE="#0A1E2A",
            SURFACE_ALT="#0F2A39",
            GLASS="rgba(120,225,255,0.06)",
            GLASS_HOVER="rgba(120,225,255,0.115)",
            BORDER="rgba(130,230,255,0.16)",
            BORDER_ACTIVE="#3FD8F5",
            PRIMARY="#1FB4EC",
            GREEN="#3FE8B2",
            PURPLE="#7F9CFF",
            ORANGE="#FFC56B",
            RED="#FF7B8B",
            TEXT="#EAFBFF",
            TEXT_SECONDARY="#86ABBB",
        ),
        style=dict(GLASS, CARD_TINT=0.15, GLOW=0.6, RIM=0.8),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (20, 184, 166, 62, 540, 0.18, 0.90, 0.08, 120, 50),
                (34, 211, 238, 44, 500, 0.75, 0.20, 0.10, 100, 80),
                (37, 99, 235, 56, 520, 0.45, 0.55, 0.06, 140, 90),
            ),
            RIBBONS=(
                (80, 220, 255, 42, 0.16, 0.045, 0.13, 0.16, 1.00, 1.2, -0.05),
                (60, 240, 200, 28, 0.30, 0.050, 0.10, 0.13, 0.75, 3.4, -0.10),
            ),
            PARTICLES="bubbles",
            PARTICLE_COUNT=26,
            PARTICLE_ALPHA=0.55,
            PARTICLE_COLOR=(170, 240, 255),
            SHOOTING_STARS=False,
            BANNER="ocean",
        ),
    ),
    "borealis": theme(
        name="Borealis",
        icon="aurora",
        tagline="Northern lights",
        description="Vivid northern lights over a frozen night sky.",
        colors=dict(
            BACKGROUND="#030A0F",
            SECONDARY="#0A2A24",
            SURFACE="#08161A",
            SURFACE_ALT="#0D2126",
            GLASS="rgba(120,255,200,0.055)",
            GLASS_HOVER="rgba(120,255,200,0.11)",
            BORDER="rgba(130,255,210,0.16)",
            BORDER_ACTIVE="#5CF0B0",
            PRIMARY="#2FD6A0",
            GREEN="#7DF0A0",
            PURPLE="#B08CFF",
            ORANGE="#FFD27A",
            RED="#FF7A9A",
            TEXT="#EAFFF6",
            TEXT_SECONDARY="#83AA9B",
        ),
        style=dict(GLASS, CARD_TINT=0.15, GLOW=0.7, RIM=0.8),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (40, 220, 160, 58, 560, 0.20, 0.15, 0.09, 110, 60),
                (120, 90, 255, 44, 520, 0.80, 0.20, 0.10, 100, 70),
                (30, 160, 220, 38, 500, 0.50, 0.95, 0.07, 120, 50),
            ),
            RIBBONS=(
                (60, 255, 170, 92, 0.16, 0.07, 0.16, 0.22, 0.90, 0.0, -0.08),
                (110, 255, 210, 60, 0.26, 0.06, 0.12, 0.18, 0.70, 1.7, -0.14),
                (150, 110, 255, 58, 0.36, 0.07, 0.12, 0.15, 0.60, 3.0, -0.06),
                (255, 120, 220, 34, 0.10, 0.05, 0.09, 0.25, 1.10, 4.2, -0.04),
            ),
            PARTICLE_COUNT=100,
            PARTICLE_ALPHA=0.7,
            PARTICLE_COLOR=(230, 255, 245),
            BANNER="mountains",
        ),
    ),
    "astro": theme(
        name="Astro",
        icon="planet",
        tagline="Solar system",
        description="The solar system: a burning sun, all eight planets in order, drifting meteors.",
        colors=dict(
            BACKGROUND="#05050E",
            SECONDARY="#0E0B1F",
            SURFACE="#0B0A18",
            SURFACE_ALT="#141026",
            GLASS="rgba(255,225,190,0.05)",
            GLASS_HOVER="rgba(255,225,190,0.10)",
            BORDER="rgba(255,215,170,0.15)",
            BORDER_ACTIVE="#FFB067",
            PRIMARY="#FF9A3D",
            GREEN="#5EE6B0",
            PURPLE="#A08CFF",
            ORANGE="#FFD166",
            RED="#FF6B6B",
            TEXT="#FFF7EC",
            TEXT_SECONDARY="#B3A796",
        ),
        style=dict(GLASS, CARD_TINT=0.14, GLOW=0.7, RIM=0.8),
        atmosphere=dict(
            KIND="astro",
            PARTICLE_COUNT=130,
            PARTICLE_ALPHA=0.8,
            PARTICLE_COLOR=(255, 244, 225),
            SHOOT_FRAMES=(150, 420),
            BANNER="orbit",
        ),
    ),
    "synthwave": theme(
        name="Synthwave",
        icon="sunset",
        tagline="Neon sunset",
        description="Retro neon: a striped sunset over a glowing grid.",
        colors=dict(
            BACKGROUND="#0E0518",
            SECONDARY="#2A0B45",
            SURFACE="#160A26",
            SURFACE_ALT="#1E0F36",
            GLASS="rgba(255,120,220,0.06)",
            GLASS_HOVER="rgba(255,120,220,0.12)",
            BORDER="rgba(255,120,230,0.20)",
            BORDER_ACTIVE="#FF5CC0",
            PRIMARY="#FF2E97",
            GREEN="#2DE2E6",
            PURPLE="#B266FF",
            ORANGE="#FFB800",
            RED="#FF4D6D",
            TEXT="#FFF0FA",
            TEXT_SECONDARY="#BE9AD6",
        ),
        style=dict(GLASS, CARD_TINT=0.15, GLOW=0.85, RIM=0.9),
        atmosphere=dict(
            KIND="synthwave",
            PARTICLE_COUNT=60,
            PARTICLE_COLOR=(255, 225, 250),
            SHOOTING_STARS=False,
            BANNER="grid",
        ),
    ),
    "ember": theme(
        name="Ember",
        icon="flame",
        tagline="Warm sparks",
        description="Charcoal dark with a slow glow and rising sparks.",
        colors=dict(
            BACKGROUND="#0B0504",
            SECONDARY="#241008",
            SURFACE="#150A07",
            SURFACE_ALT="#1E100B",
            GLASS="rgba(255,160,100,0.055)",
            GLASS_HOVER="rgba(255,160,100,0.11)",
            BORDER="rgba(255,170,110,0.16)",
            BORDER_ACTIVE="#FF8A4C",
            PRIMARY="#FF6A2E",
            GREEN="#7ED9A0",
            PURPLE="#E08CFF",
            ORANGE="#FFC34D",
            RED="#FF4D4D",
            TEXT="#FFF3EA",
            TEXT_SECONDARY="#B49A8A",
        ),
        style=dict(GLASS, CARD_TINT=0.14, GLOW=0.75, RIM=0.8),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (255, 100, 40, 60, 560, 0.15, 1.00, 0.08, 120, 40),
                (255, 160, 60, 44, 520, 0.85, 1.05, 0.10, 100, 40),
                (180, 40, 20, 40, 500, 0.50, 0.20, 0.07, 100, 60),
            ),
            RIBBONS=((255, 90, 40, 46, 0.88, 0.04, 0.10, 0.20, 0.90, 0.0, 0.03),),
            PARTICLES="embers",
            PARTICLE_COUNT=55,
            PARTICLE_ALPHA=0.9,
            PARTICLE_COLOR=(255, 170, 80),
            SHOOTING_STARS=False,
            BANNER="mountains",
        ),
    ),
    "forest": theme(
        name="Forest",
        icon="tree",
        tagline="Night woods",
        description="A quiet forest at night, drifting fireflies under the moon.",
        colors=dict(
            BACKGROUND="#040C09",
            SECONDARY="#0C2117",
            SURFACE="#08150F",
            SURFACE_ALT="#0E1F17",
            GLASS="rgba(150,255,190,0.05)",
            GLASS_HOVER="rgba(150,255,190,0.10)",
            BORDER="rgba(150,240,190,0.15)",
            BORDER_ACTIVE="#5FE39B",
            PRIMARY="#35C78A",
            GREEN="#A6E34F",
            PURPLE="#8FA8FF",
            ORANGE="#F7C948",
            RED="#FF7A7A",
            TEXT="#EDFFF5",
            TEXT_SECONDARY="#88A897",
        ),
        style=dict(GLASS, CARD_TINT=0.13, GLOW=0.55, RIM=0.75),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (30, 160, 110, 56, 560, 0.20, 0.90, 0.08, 110, 50),
                (20, 90, 80, 50, 520, 0.80, 0.30, 0.07, 100, 70),
                (220, 255, 200, 16, 420, 0.85, 0.08, 0.05, 50, 40),
            ),
            PARTICLES="fireflies",
            PARTICLE_COUNT=34,
            PARTICLE_ALPHA=0.9,
            PARTICLE_COLOR=(220, 255, 120),
            SHOOTING_STARS=False,
            BANNER="forest",
        ),
    ),
    "snow": theme(
        name="Snow",
        icon="snowflake",
        tagline="Winter calm",
        description="Soft falling snow on a cold blue evening.",
        colors=dict(
            BACKGROUND="#08101C",
            SECONDARY="#15243D",
            SURFACE="#0E1828",
            SURFACE_ALT="#152238",
            GLASS="rgba(200,225,255,0.06)",
            GLASS_HOVER="rgba(200,225,255,0.115)",
            BORDER="rgba(200,225,255,0.17)",
            BORDER_ACTIVE="#8FC2FF",
            PRIMARY="#6FAEFF",
            GREEN="#6EE7C8",
            PURPLE="#B3A6FF",
            ORANGE="#FFD08A",
            RED="#FF8FA3",
            TEXT="#F3F8FF",
            TEXT_SECONDARY="#8EA3BF",
        ),
        style=dict(GLASS, CARD_TINT=0.12, GLOW=0.5, RIM=0.9),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=(
                (140, 190, 255, 44, 560, 0.20, 0.20, 0.07, 100, 60),
                (200, 220, 255, 26, 520, 0.85, 0.90, 0.06, 100, 50),
            ),
            PARTICLES="snow",
            PARTICLE_COUNT=90,
            PARTICLE_ALPHA=0.85,
            PARTICLE_COLOR=(240, 248, 255),
            SHOOTING_STARS=False,
            BANNER="snow",
        ),
    ),
    "mono": theme(
        name="Mono",
        icon="contrast",
        tagline="Pure black and white",
        description="Strictly monochrome. No colour, no distraction.",
        colors=dict(
            BACKGROUND="#060606",
            SECONDARY="#141414",
            SURFACE="#0D0D0D",
            SURFACE_ALT="#171717",
            GLASS="rgba(255,255,255,0.04)",
            GLASS_HOVER="rgba(255,255,255,0.08)",
            BORDER="rgba(255,255,255,0.10)",
            BORDER_ACTIVE="#CFCFCF",
            PRIMARY="#8A8A8A",
            GREEN="#7C7C7C",
            PURPLE="#A5A5A5",
            ORANGE="#B8B8B8",
            RED="#F2F2F2",
            TEXT="#F0F0F0",
            TEXT_SECONDARY="#828282",
        ),
        style=dict(GLASS, CARD_TINT=0.08, GLOW=0.0, RIM=0.35, PANEL_TINT=False),
        atmosphere=dict(
            KIND="aurora",
            BLOBS=((255, 255, 255, 10, 600, 0.15, 0.15, 0.05, 80, 50),),
            PARTICLE_COUNT=40,
            PARTICLE_ALPHA=0.4,
            SHOOTING_STARS=False,
            BANNER="wave",
        ),
    ),
    "light": theme(
        name="Light",
        icon="sun",
        tagline="Clean and bright",
        description="Clean and bright, calm white glass.",
        colors=dict(
            BACKGROUND="#F6F7FB",
            SECONDARY="#EEF1F7",
            SURFACE="#FFFFFF",
            SURFACE_ALT="#F0F2F8",
            GLASS="rgba(0,0,0,0.04)",
            GLASS_HOVER="rgba(0,0,0,0.08)",
            BORDER="rgba(0,0,0,0.08)",
            BORDER_ACTIVE="#4C6FFF",
            PRIMARY="#4C6FFF",
            GREEN="#34C759",
            PURPLE="#AF52DE",
            ORANGE="#FF9500",
            RED="#FF3B30",
            TEXT="#111318",
            TEXT_SECONDARY="#687086",
        ),
        atmosphere=dict(KIND="none"),
        qss=light_qss,
    ),
    "sakura": theme(
        name="Sakura",
        icon="blossom",
        tagline="Blossom dusk",
        description="Cherry blossom dusk, deep plum and pink.",
        colors=dict(
            BACKGROUND="#2B1826",
            SECONDARY="#3D2136",
            SURFACE="#3A2233",
            SURFACE_ALT="#452A3F",
            GLASS="rgba(255,255,255,0.07)",
            GLASS_HOVER="rgba(255,255,255,0.12)",
            BORDER="rgba(255,255,255,0.12)",
            BORDER_ACTIVE="#FF6FA5",
            PRIMARY="#FF4D94",
            GREEN="#6FCF97",
            PURPLE="#8B7FE8",
            ORANGE="#FFAE5C",
            RED="#FF6B81",
            TEXT="#FDF3F8",
            TEXT_SECONDARY="#CBA3B8",
        ),
        atmosphere=dict(KIND="sakura", BANNER="mountains"),
        qss=sakura_qss,
    ),
}
