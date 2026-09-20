from themes.manager import ThemeManager


class Theme:

    @classmethod
    def set(cls, name):

        ThemeManager.set_theme(name)


    @classmethod
    def current(cls):

        return ThemeManager.get()


    @classmethod
    def stylesheet(cls):

        return ThemeManager.stylesheet()