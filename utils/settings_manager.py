from database.database import Database


class SettingsManager:

    # Thin wrapper over Database's settings table, mirroring how
    # TaskManager wraps task rows. Every page that needs a setting
    # creates its own instance — same pattern as TaskManager, and
    # fine for the same reason: SQLite handles multiple connections
    # to one file without issue.

    def __init__(self):

        self.database = Database()


    def get(self, key, default=None):

        return self.database.get_setting(key, default)


    def set(self, key, value):

        self.database.set_setting(key, value)


    def get_user_name(self):

        return self.database.get_setting("user_name", "") or ""


    def set_user_name(self, name):

        self.database.set_setting("user_name", (name or "").strip())


    def get_lock_screen_enabled(self):

        value = self.database.get_setting("lock_screen_enabled", "1")

        return value == "1"


    def set_lock_screen_enabled(self, enabled):

        self.database.set_setting(
            "lock_screen_enabled",
            "1" if enabled else "0"
        )


    def get_theme(self):

        return self.database.get_setting("theme", "dark") or "dark"


    def set_theme(self, name):

        self.database.set_setting("theme", name)


    def get_notes_pin_hash(self):

        return self.database.get_setting("notes_pin_hash", "") or ""


    def set_notes_pin_hash(self, pin_hash):

        self.database.set_setting("notes_pin_hash", pin_hash)


    def close(self):

        self.database.close()
