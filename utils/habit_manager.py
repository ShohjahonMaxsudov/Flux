from datetime import datetime, timedelta

from database.database import Database


class HabitManager:

    def __init__(self):

        self.database = Database()


    def get_habits(self):

        return [
            dict(row)
            for row in self.database.get_habits()
        ]


    def get_habits_with_week(self):

        monday = (
            datetime.now()
            - timedelta(days=datetime.now().weekday())
        ).date()

        result = []

        for habit in self.get_habits():

            week = []

            for offset in range(7):

                day = monday + timedelta(days=offset)
                day_iso = day.strftime("%Y-%m-%d")

                week.append(
                    (
                        day_iso,
                        self.database.get_habit_day(
                            habit["id"],
                            day_iso
                        )
                    )
                )

            habit["week"] = week
            result.append(habit)

        return result


    def toggle_day(self, habit_id, day_iso):

        current = self.database.get_habit_day(
            habit_id,
            day_iso
        )

        self.database.set_habit_day(
            habit_id,
            day_iso,
            not current
        )


    def week_completion_percent(self):

        habits = self.get_habits_with_week()

        if not habits:
            return 0

        total = len(habits) * 7

        completed = sum(
            1
            for habit in habits
            for _day, checked in habit["week"]
            if checked
        )

        return round(
            (completed / total) * 100
        )


    def close(self):

        self.database.close()
