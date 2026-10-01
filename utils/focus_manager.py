from datetime import datetime, timedelta

from database.database import Database


class FocusManager:

    # Wraps the focus_sessions table the same way TaskManager wraps
    # tasks — one instance per page/widget that needs it, same as the
    # rest of the app; SQLite handles the shared connections fine.

    def __init__(self):

        self.database = Database()


    def log_session(self, minutes):

        if minutes <= 0:
            return None

        today = datetime.now().strftime("%Y-%m-%d")

        return self.database.add_focus_session(
            minutes,
            today
        )


    def _rows_since(self, days):

        cutoff = (
            datetime.now() - timedelta(days=days - 1)
        ).date()

        rows = self.database.get_focus_sessions()

        result = []

        for row in rows:

            try:

                day = datetime.strptime(
                    row["session_date"],
                    "%Y-%m-%d"
                ).date()

            except (ValueError, TypeError):

                continue

            if day >= cutoff:

                result.append((day, row["minutes"]))

        return result


    def get_today_minutes(self):

        today = datetime.now().date()

        return sum(
            minutes
            for day, minutes in self._rows_since(1)
            if day == today
        )


    def get_week_minutes(self):

        monday = (
            datetime.now()
            - timedelta(days=datetime.now().weekday())
        ).date()

        return sum(
            minutes
            for day, minutes in self._rows_since(7)
            if day >= monday
        )


    def close(self):

        self.database.close()
