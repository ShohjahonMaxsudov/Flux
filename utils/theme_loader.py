from themes import dark
from themes import light
from themes import sakura


class ThemeLoader:


    themes = {

        "Midnight": dark,

        "Arctic Light": light,

        "Sakura": sakura

    }


    current = dark



    @classmethod
    def load(
        cls,
        name
    ):

        if name in cls.themes:

            cls.current = cls.themes[name]


        return cls.current



    @classmethod
    def get(
        cls
    ):

        return cls.current



    @classmethod
    def stylesheet(
        cls
    ):

        return cls.current.GLOBAL_STYLESHEET