"""
Flux branding: sidebar logo, app/window icon, and the tiny credits strip
at the bottom of Settings.

Assets live in <project>/assets (bundled next to the code when frozen with
PyInstaller: --add-data "assets;assets").
"""

import sys
from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def resource_path(relative):

    # Works both from source and from a frozen (PyInstaller) build.

    bundle = getattr(sys, "_MEIPASS", None)

    root = Path(bundle) if bundle else Path(__file__).resolve().parent.parent

    return str(root / relative)


# ---------------------------------------------------------------------------
# App icon
# ---------------------------------------------------------------------------

def apply_app_identity(app, app_id="ianfn.flux.desktop"):

    # Window + taskbar icon. On Windows the taskbar groups an app under its
    # process's AppUserModelID; without setting one it shows the generic
    # Python/launcher icon instead of ours.

    if sys.platform == "win32":

        try:

            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                app_id
            )

        except Exception:

            pass

    icon = QIcon(resource_path("assets/flux.ico"))

    if icon.isNull():

        icon = QIcon(resource_path("assets/flux_icon.png"))

    app.setWindowIcon(icon)


# ---------------------------------------------------------------------------
# Sidebar logo
# ---------------------------------------------------------------------------

class FluxLogo(QWidget):

    # Flux wordmark with its sparkle glow. Both variants are transparent
    # PNGs, so the aurora / starfield / sakura background shows through the
    # glow. "dark" is the white wordmark (dark + sakura themes); "light" is
    # an ink-coloured version so the logo doesn't disappear on white.

    def __init__(self, width=214, variant="dark", parent=None):

        super().__init__(parent)

        self._pixmaps = {
            name: QPixmap(resource_path(f"assets/flux_logo_{name}.png"))
            for name in ("dark", "light")
        }

        self._variant = variant

        self._cache = None

        source = self._pixmaps[variant]

        ratio = source.height() / max(1, source.width())

        self.setFixedSize(width, round(width * ratio))

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


    def set_variant(self, variant):

        if variant == self._variant or variant not in self._pixmaps:
            return

        self._variant = variant

        self._cache = None

        self.update()


    def set_theme(self, theme_name):

        self.set_variant(
            "light" if theme_name == "light" else "dark"
        )


    def _scaled(self):

        dpr = self.devicePixelRatioF()

        w = round(self.width() * dpr)

        h = round(self.height() * dpr)

        key = (self._variant, w, h)

        if self._cache is None or self._cache[0] != key:

            pm = self._pixmaps[self._variant].scaled(
                w,
                h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            pm.setDevicePixelRatio(dpr)

            self._cache = (key, pm)

        return self._cache[1]


    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.SmoothPixmapTransform
        )

        painter.drawPixmap(0, 0, self._scaled())

        painter.end()


# ---------------------------------------------------------------------------
# Credits strip (Settings, bottom)
# ---------------------------------------------------------------------------

# Glyph paths: Bootstrap Icons (MIT), 16x16 viewBox.

_GLYPHS = {

    "telegram": (
        "M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M8.287 5.906q-1.168.486-4.666 2.01-.567.225-.595.442"
        "c-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294q.39.01.868-.32 3.269-2.206 "
        "3.374-2.23c.05-.012.12-.026.166.016s.042.12.037.141c-.03.129-1.227 1.241-1.846 1.817"
        "-.193.18-.33.307-.358.336a8 8 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393"
        ".85.571.284.194.568.387.936.629q.14.092.27.187c.331.236.63.448.997.414.214-.02.435-.22"
        ".547-.82.265-1.417.786-4.486.906-5.751a1.4 1.4 0 0 0-.013-.315.34.34 0 0 0-.114-.217"
        ".53.53 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09"
    ),

    "instagram": (
        "M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.9 3.9 0 0 0-1.417.923A3.9 "
        "3.9 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444"
        ".048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923"
        ".51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434"
        "-.174 1.943-.372a3.9 3.9 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09"
        ".372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372"
        "-1.941a3.9 3.9 0 0 0-.923-1.417A3.9 3.9 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372"
        "C10.443.01 10.172 0 7.998 0zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204"
        ".166 1.486.275.373.145.64.319.92.599s.453.546.598.92c.11.281.24.705.275 1.485.039.843"
        ".047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.5 2.5 0 0 "
        "1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232"
        ".047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.5 2.5 0 0 1-.92-.598 2.5 "
        "2.5 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233s.008"
        "-2.388.046-3.231c.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92s.546-.453.92"
        "-.598c.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045zm4.988 1.328a.96.96 0 "
        "1 0 0 1.92.96.96 0 0 0 0-1.92m-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 "
        "0-8.217m0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334"
    ),

    "discord": (
        "M13.545 2.907a13.2 13.2 0 0 0-3.257-1.011.05.05 0 0 0-.052.025c-.141.25-.297.577-.406"
        ".833a12.2 12.2 0 0 0-3.658 0 8 8 0 0 0-.412-.833.05.05 0 0 0-.052-.025c-1.125.194-2.22"
        ".534-3.257 1.011a.04.04 0 0 0-.021.018C.356 6.024-.213 9.047.066 12.032q.003.022.021.037"
        "a13.3 13.3 0 0 0 3.995 2.02.05.05 0 0 0 .056-.019q.463-.63.818-1.329a.05.05 0 0 0-.01"
        "-.059l-.018-.011a9 9 0 0 1-1.248-.595.05.05 0 0 1-.02-.066l.015-.019q.127-.095.248-.195"
        "a.05.05 0 0 1 .051-.007c2.619 1.196 5.454 1.196 8.041 0a.05.05 0 0 1 .053.007q.121.1.248"
        ".195a.05.05 0 0 1-.004.085 8 8 0 0 1-1.249.594.05.05 0 0 0-.03.03.05.05 0 0 0 .003.041"
        "c.24.465.515.909.817 1.329a.05.05 0 0 0 .056.019 13.2 13.2 0 0 0 4.001-2.02.05.05 0 0 0 "
        ".021-.037c.334-3.451-.559-6.449-2.366-9.106a.03.03 0 0 0-.02-.019m-8.198 7.307c-.789 0"
        "-1.438-.724-1.438-1.612s.637-1.613 1.438-1.613c.807 0 1.45.73 1.438 1.613 0 .888-.637 "
        "1.612-1.438 1.612m5.316 0c-.788 0-1.438-.724-1.438-1.612s.637-1.613 1.438-1.613c.807 0 "
        "1.451.73 1.438 1.613 0 .888-.631 1.612-1.438 1.612"
    ),
}


# (glyph, handle), in display order. @fluxbyian is the official changelog
# and showcase channel.

CREDITS = [
    ("telegram", "@ianfn"),
    ("instagram", "@ianvrv"),
    ("discord", "@ianvrv"),
    ("telegram", "@fluxbyian"),
]


def _glyph_pixmap(name, px, color, dpr):

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        f'<path fill="{color.name()}" fill-opacity="{color.alphaF():.3f}" '
        f'fill-rule="evenodd" d="{_GLYPHS[name]}"/></svg>'
    )

    size = max(1, round(px * dpr))

    pm = QPixmap(size, size)

    pm.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pm)

    painter.setRenderHints(
        QPainter.RenderHint.Antialiasing
        | QPainter.RenderHint.SmoothPixmapTransform
    )

    QSvgRenderer(QByteArray(svg.encode("utf-8"))).render(painter)

    painter.end()

    pm.setDevicePixelRatio(dpr)

    return pm


class CreditsFooter(QWidget):

    # Purely decorative "made by" strip. It ignores the mouse completely -
    # no clicks, no hover, no cursor change, no selectable text - so nobody
    # opens a link by accident.

    def __init__(self, icon_px=9, font_px=8, opacity=0.42, parent=None):

        super().__init__(parent)

        self._icon_px = icon_px

        self._font_px = font_px

        self._opacity = opacity

        self._color = QColor("#FFFFFF")

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


        row = QHBoxLayout(self)

        row.setContentsMargins(0, 0, 0, 0)

        row.setSpacing(11)


        self._icons = []

        self._texts = []

        for glyph, handle in CREDITS:

            cell = QWidget(self)

            cell.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            cellLayout = QHBoxLayout(cell)

            cellLayout.setContentsMargins(0, 0, 0, 0)

            cellLayout.setSpacing(3)


            icon = QLabel(cell)

            icon.setFixedSize(icon_px, icon_px)

            icon.setStyleSheet("background:transparent; border:none;")


            text = QLabel(handle, cell)

            text.setTextFormat(Qt.TextFormat.PlainText)

            text.setTextInteractionFlags(
                Qt.TextInteractionFlag.NoTextInteraction
            )


            for widget in (icon, text):

                widget.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents
                )

                widget.setCursor(Qt.CursorShape.ArrowCursor)


            cellLayout.addWidget(icon)

            cellLayout.addWidget(text)

            row.addWidget(cell)

            self._icons.append((icon, glyph))

            self._texts.append(text)


        self._render()


    def set_color(self, color):

        # `color` is the theme's text colour (any QColor-parsable string);
        # the strip draws it at low opacity so it reads as a signature,
        # not as UI.

        self._color = QColor(color)

        self._render()


    def _render(self):

        c = QColor(self._color)

        c.setAlphaF(self._opacity)

        css = f"rgba({c.red()},{c.green()},{c.blue()},{c.alpha()})"

        screen = QApplication.primaryScreen()

        dpr = max(self.devicePixelRatioF(), screen.devicePixelRatio() if screen else 1.0)

        for icon, glyph in self._icons:

            icon.setPixmap(
                _glyph_pixmap(glyph, self._icon_px, c, dpr)
            )

        for text in self._texts:

            text.setStyleSheet(
                f"background:transparent; border:none; color:{css}; "
                f"font-size:{self._font_px}px;"
            )


    def showEvent(self, event):

        super().showEvent(event)

        self._render()
