from datetime import datetime, timedelta

from database.database import Database
from database.models import Task



class TaskManager:


    def __init__(self):

        self.database = Database()



    # -----------------------------
    # CREATE
    # -----------------------------


    def create_task(
        self,
        title,
        time="",
        task_date="",
        priority="Normal",
        category="General",
        description="",
        color="#5A7DFF",
        reminder="None",
        repeat="Never",
        important=False
    ):

        # Forwarded as keyword arguments on purpose: Database.add_task's
        # parameter order doesn't match this method's, and the previous
        # positional call (self.database.add_task(title, time, priority,
        # category)) silently posted "priority" into the task_date slot
        # and "category" into the priority slot. Keyword args make that
        # class of bug impossible even if either signature changes again.

        self.database.add_task(
            title=title,
            time=time,
            task_date=task_date,
            priority=priority,
            category=category,
            description=description,
            color=color,
            reminder=reminder,
            repeat=repeat,
            important=important
        )



    # -----------------------------
    # READ
    # -----------------------------


    def get_all_tasks(self):

        rows = self.database.get_tasks()


        tasks = [
            Task.from_row(row)
            for row in rows
        ]


        tasks.sort(
            key=lambda task: (
                task.completed,
                task.priority_order
            )
        )


        return tasks



    def get_today_tasks(self):

        today = datetime.now().date()


        rows = self.database.get_tasks()


        result = []


        for row in rows:

            created = row["created_at"]


            try:

                task_date = datetime.strptime(
                    created,
                    "%Y-%m-%d %H:%M:%S"
                ).date()


                if task_date == today:

                    result.append(
                        Task.from_row(row)
                    )


            except:

                pass



        return result



    # -----------------------------
    # STREAK
    # -----------------------------


    def calculate_streak(self):

        rows = self.database.get_tasks()


        completed_days = set()


        for row in rows:

            if row["completed"]:

                try:

                    date = datetime.strptime(
                        row["created_at"],
                        "%Y-%m-%d %H:%M:%S"
                    ).date()


                    completed_days.add(
                        date
                    )


                except:

                    pass



        if not completed_days:

            return 0



        streak = 0

        day = datetime.now().date()



        while day in completed_days:

            streak += 1

            day -= timedelta(
                days=1
            )


        return streak



    # -----------------------------
    # FILTERS
    # -----------------------------


    def get_tasks_by_category(
        self,
        category
    ):

        if category == "All":

            return self.get_all_tasks()


        return [

            task

            for task in self.get_all_tasks()

            if task.category == category

        ]



    def search_tasks(
        self,
        text
    ):

        text = text.lower()


        return [

            task

            for task in self.get_all_tasks()

            if text in task.title.lower()

        ]



    # -----------------------------
    # UPDATE
    # -----------------------------


    def edit_task(
        self,
        task_id,
        title,
        time="",
        task_date="",
        priority="Normal",
        category="General",
        description="",
        color="#5A7DFF",
        reminder="None",
        repeat="Never",
        important=False
    ):

        self.database.update_task(
            task_id=task_id,
            title=title,
            time=time,
            task_date=task_date,
            priority=priority,
            category=category,
            description=description,
            color=color,
            reminder=reminder,
            repeat=repeat,
            important=important
        )



    def complete_task(
        self,
        task_id,
        completed
    ):

        self.database.update_task_status(
            task_id,
            completed
        )



    # -----------------------------
    # DELETE
    # -----------------------------


    def remove_task(
        self,
        task_id
    ):

        self.database.delete_task(
            task_id
        )



    # -----------------------------
    # STATISTICS
    # -----------------------------


    def get_statistics(self):

        tasks = self.get_all_tasks()


        today = self.get_today_tasks()


        completed = [

            task

            for task in tasks

            if task.completed

        ]


        return {

            "total": len(today),

            "completed": len(completed),

            "pending": len(today) - len(

                [

                task

                for task in today

                if task.completed

                ]

            ),

            "streak": self.calculate_streak()

        }



    def close(self):

        self.database.close()