from datetime import datetime, timedelta

from database.database import Database


class HabitManager:

    def __init__(self):

        self.database = Database()


    def create_habit(self, name, color="#5A7DFF"):

        name = (name or "").strip()

        if not name:
            return None

        return self.database.add_habit(
            name,
            color
        )


    def delete_habit(self, habit_id):

        self.database.delete_habit(
            habit_id
        )


    def get_habits(self):

        return [
            dict(row)
            for row in self.database.get_habits()
        ]


    def week_days(self):

        today = datetime.now().date()

        monday = today - timedelta(
            days=today.weekday()
        )

        return [
            monday + timedelta(days=offset)
            for offset in range(7)
        ]


    def habits_with_week(self):

        days = self.week_days()

        result = []

        for habit in self.get_habits():

            habit["week"] = [
                (
                    day.strftime("%Y-%m-%d"),
                    self.database.get_habit_day(
                        habit["id"],
                        day.strftime("%Y-%m-%d")
                    )
                )
                for day in days
            ]

            result.append(habit)

        return result


    def toggle_day(self, habit_id, day):

        current = self.database.get_habit_day(
            habit_id,
            day
        )

        self.database.set_habit_day(
            habit_id,
            day,
            not current
        )

        return not current


    def weekly_completion(self):

        habits = self.habits_with_week()

        if not habits:
            return 0

        done = sum(
            1
            for habit in habits
            for _day, completed in habit["week"]
            if completed
        )

        total = len(habits) * 7

        return round(
            done / total * 100
        ) if total else 0


    def completed_today(self):

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        return sum(
            1
            for habit in self.get_habits()
            if self.database.get_habit_day(
                habit["id"],
                today
            )
        )


    def best_streak(self):

        best = 0

        for habit in self.get_habits():

            days = [
                datetime.strptime(
                    row["day"],
                    "%Y-%m-%d"
                ).date()
                for row in self.database.get_habit_logs(
                    habit["id"]
                )
            ]

            if not days:
                continue

            days = sorted(
                set(days)
            )

            streak = 1

            best = max(
                best,
                streak
            )

            for previous, current in zip(
                days,
                days[1:]
            ):

                if current - previous == timedelta(days=1):

                    streak += 1

                else:

                    streak = 1

                best = max(
                    best,
                    streak
                )

        return best


    def close(self):

        self.database.close()
