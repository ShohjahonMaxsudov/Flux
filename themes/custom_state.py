from utils.settings_manager import SettingsManager


class CustomState:

    # The Custom theme's two knobs, persisted in the settings table.
    # Loaded lazily (first time anything asks) rather than at import,
    # so importing themes.custom doesn't open a database connection
    # unless the Custom theme is actually touched.

    primary = "#5A7DFF"

    glow = 0.65

    _loaded = False


    @classmethod
    def _ensure_loaded(cls):

        if cls._loaded:
            return

        cls._loaded = True

        manager = SettingsManager()

        cls.primary = manager.get(
            "custom_theme_primary",
            cls.primary
        ) or cls.primary

        try:

            cls.glow = float(
                manager.get(
                    "custom_theme_glow",
                    str(cls.glow)
                )
            )

        except (TypeError, ValueError):

            pass

        manager.close()


    @classmethod
    def get(cls):

        cls._ensure_loaded()

        return cls.primary, cls.glow


    @classmethod
    def set(cls, primary=None, glow=None):

        cls._ensure_loaded()

        if primary is not None:

            cls.primary = primary

        if glow is not None:

            cls.glow = max(0.0, min(1.0, glow))

        manager = SettingsManager()

        manager.set("custom_theme_primary", cls.primary)

        manager.set("custom_theme_glow", str(cls.glow))

        manager.close()
