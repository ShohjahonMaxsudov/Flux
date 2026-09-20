from PySide6.QtCore import QObject, Signal

from themes import dark
from themes import light
from themes import sakura


class _ThemeSignal(QObject):

    # A plain classmethod-based manager has nowhere to emit a Qt
    # signal from, so the notification lives on a small QObject
    # instead. This is what lets the main window swap its animated
    # background (aurora/starfield vs. the Sakura atmosphere) and
    # refresh other live widgets the moment the theme changes,
    # instead of only the widget that triggered the change updating
    # itself.

    changed = Signal(str)


class ThemeManager:

    themes = {
        "dark": dark,
        "light": light,
        "sakura": sakura
    }


    current_name = "dark"

    _signal = _ThemeSignal()


    @classmethod
    def set_theme(cls, name):

        if name not in cls.themes:
            return

        if name == cls.current_name:
            return

        cls.current_name = name

        cls._signal.changed.emit(name)


    @classmethod
    def subscribe(cls, slot):

        cls._signal.changed.connect(slot)


    @classmethod
    def get(cls):

        return cls.themes[cls.current_name]


    @classmethod
    def stylesheet(cls):

        theme = cls.get()

        return theme.GLOBAL_STYLESHEET
