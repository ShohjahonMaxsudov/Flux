from database.database import Database


class MilestoneManager:

    def __init__(self):

        self.database = Database()


    def create(
        self,
        title,
        target=100,
        due_date="",
        color="#5A7DFF"
    ):

        return self.database.add_milestone(
            title=(title or "").strip(),
            target=target,
            due_date=due_date,
            color=color
        )


    def all(self):

        return [
            dict(row)
            for row in self.database.get_milestones()
        ]


    def set_progress(
        self,
        milestone_id,
        progress
    ):

        self.database.update_milestone_progress(
            milestone_id,
            progress
        )


    def delete(
        self,
        milestone_id
    ):

        self.database.delete_milestone(
            milestone_id
        )


    def close(self):

        self.database.close()
