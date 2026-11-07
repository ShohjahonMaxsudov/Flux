from PySide6.QtCore import QObject, Signal

from themes.catalog import THEMES
from themes.custom import CUSTOM


class _ThemeSignal(QObject):
    # A classmethod-based manager has nowhere to emit a Qt signal from, so the
    # notifications live on this small QObject instead. That is what lets the
    # main window swap its animated background and refresh other live widgets
    # the moment the theme changes.
    # fires *before* the switch (old, new) so the main window can snapshot the
    # old look and cross-fade to the new one
    aboutToChange = Signal(str, str)
    changed = Signal(str)

    # fires when the CURRENT theme's own parameters change (the Custom theme's
    # colour or glow slider being tweaked live) rather than switching to a
    # different theme. Listeners repaint the same way but skip the cross-fade.
    styleChanged = Signal(str)


class ThemeManager:
    # Order here is the order shown in the picker, and the order the header's
    # theme button cycles through.
    themes = {**THEMES, "custom": CUSTOM}
    current_name = "dark"
    _signal = _ThemeSignal()

    @classmethod
    def set_theme(cls, name):
        if name not in cls.themes or name == cls.current_name:
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
        # For a theme tweaking its own live parameters (Custom's colour / glow),
        # not for switching themes - see styleChanged.
        cls._signal.styleChanged.emit(cls.current_name)

    @classmethod
    def get(cls, name=None):
        # An unknown name falls back to "dark".
        return cls.themes.get(name or cls.current_name, THEMES["dark"])

    @classmethod
    def stylesheet(cls):
        return cls.get().GLOBAL_STYLESHEET

    @classmethod
    def style(cls, name=None):
        return cls.get(name).Style

    @classmethod
    def atmosphere(cls, name=None):
        return cls.get(name).Atmosphere

    # -- picker / header button / lock screen metadata
    @classmethod
    def names(cls):
        return list(cls.themes)

    @classmethod
    def label(cls, name):
        return cls.themes[name].NAME

    @classmethod
    def icon(cls, name):
        return cls.themes[name].ICON

    @classmethod
    def description(cls, name):
        return cls.themes[name].DESCRIPTION

    @classmethod
    def tagline(cls, name):
        return cls.themes[name].TAGLINE

    @classmethod
    def next_name(cls):
        names = cls.names()

        if cls.current_name not in names:
            return names[0]

        return names[(names.index(cls.current_name) + 1) % len(names)]
