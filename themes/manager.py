from PySide6.QtCore import QObject, Signal

from themes import base
from themes import dark
from themes import nebula
from themes import void
from themes import ocean
from themes import borealis
from themes import astro
from themes import synthwave
from themes import ember
from themes import forest
from themes import snow
from themes import mono
from themes import light
from themes import sakura
from themes import custom


class _ThemeSignal(QObject):

    # A plain classmethod-based manager has nowhere to emit a Qt
    # signal from, so the notification lives on a small QObject
    # instead. This is what lets the main window swap its animated
    # background (aurora/starfield vs. the Sakura atmosphere) and
    # refresh other live widgets the moment the theme changes,
    # instead of only the widget that triggered the change updating
    # itself.
    #
    # aboutToChange fires *before* the switch (old, new) so the main
    # window can snapshot the old look and cross-fade to the new one.

    changed = Signal(str)

    aboutToChange = Signal(str, str)

    # Fired when the CURRENT theme's own parameters change - the
    # Custom theme's color or glow slider being tweaked live -
    # rather than switching to a different theme. Listeners repaint
    # everything the same way, but skip the cross-fade: nothing is
    # actually changing identity, so a snap update reads as
    # responsive tuning instead of a jarring transition.

    styleChanged = Signal(str)


class ThemeManager:

    # Order here is the order shown in the picker and the order the
    # header's theme button cycles through.

    themes = {
        "dark": dark,
        "nebula": nebula,
        "void": void,
        "ocean": ocean,
        "borealis": borealis,
        "astro": astro,
        "synthwave": synthwave,
        "ember": ember,
        "forest": forest,
        "snow": snow,
        "mono": mono,
        "light": light,
        "sakura": sakura,
        "custom": custom
    }


    current_name = "dark"

    _signal = _ThemeSignal()


    @classmethod
    def set_theme(cls, name):

        if name not in cls.themes:
            return

        if name == cls.current_name:
            return

        cls._signal.aboutToChange.emit(cls.current_name, name)

        cls.current_name = name

        cls._signal.changed.emit(name)


    @classmethod
    def subscribe(cls, slot):

        cls._signal.changed.connect(slot)


    @classmethod
    def subscribe_before(cls, slot):

        cls._signal.aboutToChange.connect(slot)


    @classmethod
    def subscribe_style(cls, slot):

        cls._signal.styleChanged.connect(slot)


    @classmethod
    def refresh_current(cls):

        # For a theme tweaking its own live parameters (Custom's
        # color/glow), not for switching themes - see styleChanged.

        cls._signal.styleChanged.emit(cls.current_name)


    @classmethod
    def get(cls):

        return cls.themes.get(cls.current_name, dark)


    @classmethod
    def stylesheet(cls):

        theme = cls.get()

        return theme.GLOBAL_STYLESHEET


    # -- metadata used by the picker, header button and lock screen

    @classmethod
    def names(cls):

        return list(cls.themes)


    @classmethod
    def label(cls, name):

        return getattr(cls.themes[name], "NAME", name.title())


    @classmethod
    def icon(cls, name):

        return getattr(cls.themes[name], "ICON", "moon")


    @classmethod
    def description(cls, name):

        return getattr(cls.themes[name], "DESCRIPTION", "")


    @classmethod
    def tagline(cls, name):

        return getattr(cls.themes[name], "TAGLINE", cls.label(name))


    @classmethod
    def next_name(cls):

        names = cls.names()

        if cls.current_name not in names:

            return names[0]

        return names[(names.index(cls.current_name) + 1) % len(names)]


    # -- style / atmosphere with safe fallbacks for old-style themes

    @classmethod
    def style(cls, name=None):

        theme = cls.themes.get(name or cls.current_name, dark)

        return getattr(theme, "Style", base.Style)


    @classmethod
    def atmosphere(cls, name=None):

        theme = cls.themes.get(name or cls.current_name, dark)

        return getattr(theme, "Atmosphere", base.Atmosphere)
