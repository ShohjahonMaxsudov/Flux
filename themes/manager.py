from PySide6.QtCore import QObject, Signal

from themes import base, midnight


class _ThemeSignal(QObject):
    changed = Signal(str)
    aboutToChange = Signal(str, str)
    styleChanged = Signal(str)


class ThemeManager:
    """Compatibility layer for old pages; Flux v3 intentionally has one identity."""

    themes = {"midnight": midnight}
    current_name = "midnight"
    _signal = _ThemeSignal()

    @classmethod
    def set_theme(cls, _name):
        if cls.current_name != "midnight":
            old = cls.current_name
            cls._signal.aboutToChange.emit(old, "midnight")
            cls.current_name = "midnight"
            cls._signal.changed.emit("midnight")

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
        cls._signal.styleChanged.emit("midnight")

    @classmethod
    def get(cls):
        cls.current_name = "midnight"
        return midnight

    @classmethod
    def stylesheet(cls):
        return midnight.GLOBAL_STYLESHEET

    @classmethod
    def names(cls):
        return ["midnight"]

    @classmethod
    def label(cls, _name):
        return midnight.NAME

    @classmethod
    def icon(cls, _name):
        return midnight.ICON

    @classmethod
    def description(cls, _name):
        return midnight.DESCRIPTION

    @classmethod
    def tagline(cls, _name):
        return midnight.TAGLINE

    @classmethod
    def next_name(cls):
        return "midnight"

    @classmethod
    def style(cls, _name=None):
        return getattr(midnight, "Style", base.Style)

    @classmethod
    def atmosphere(cls, _name=None):
        return getattr(midnight, "Atmosphere", base.Atmosphere)
