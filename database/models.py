from dataclasses import dataclass


@dataclass
class Note:

    id: int

    title: str = ""

    body: str = ""

    tags: str = ""

    locked: bool = False

    pin_hash: str = ""

    created_at: str = ""

    updated_at: str = ""


    @classmethod
    def from_row(cls, row):

        keys = row.keys()


        def get(name, default=None):

            return (
                row[name]
                if name in keys
                else default
            )


        return cls(

            id=get("id"),

            title=get("title") or "",

            body=get("body") or "",

            tags=get("tags") or "",

            locked=bool(get("locked") or 0),

            pin_hash=get("pin_hash") or "",

            created_at=get("created_at") or "",

            updated_at=get("updated_at") or ""

        )


    @property
    def preview(self):

        if self.locked:

            return "Locked note"

        text = self.body.strip().replace("\n", " ")

        return (
            text[:90] + "…"
            if len(text) > 90
            else (text or "No additional text")
        )



@dataclass
class Task:

    id: int

    title: str

    time: str = ""

    task_date: str = ""

    priority: str = "Normal"

    category: str = "General"

    description: str = ""

    color: str = "#5A7DFF"

    reminder: str = "None"

    repeat: str = "Never"

    important: bool = False

    completed: bool = False

    created_at: str = ""


    @classmethod
    def from_row(cls, row):

        # IMPORTANT: read columns by NAME (row["priority"]), never by
        # positional index (row[3]).
        #
        # This table started with 7 columns and later had task_date,
        # description, color, reminder, repeat and important added via
        # ALTER TABLE. On a database that was created before that
        # migration, those new columns land at the END of the physical
        # row regardless of where they appear in CREATE TABLE. On a
        # brand-new database (fresh install, or flux.db deleted), they
        # land wherever the current CREATE TABLE statement puts them.
        # Two different, equally valid physical layouts for the same
        # logical schema — a positional Task.from_row would silently
        # read priority/category/completed from the wrong column
        # depending on which one it happened to be given. Column-name
        # access is immune to that regardless of physical column order.

        keys = row.keys()


        def get(name, default=None):

            return (
                row[name]
                if name in keys
                else default
            )


        return cls(

            id=get("id"),

            title=get("title") or "",

            time=get("time") or "",

            task_date=get("task_date") or "",

            priority=get("priority") or "Normal",

            category=get("category") or "General",

            description=get("description") or "",

            color=get("color") or "#5A7DFF",

            reminder=get("reminder") or "None",

            repeat=get("repeat") or "Never",

            important=bool(get("important") or 0),

            completed=bool(get("completed") or 0),

            created_at=get("created_at") or ""

        )


    @property
    def priority_order(self):

        mapping = {
            "High": 0,
            "Normal": 1,
            "Low": 2
        }

        return mapping.get(
            self.priority,
            1
        )


    @property
    def priority_color(self):

        colors = {

            "High": "#FF5D5D",

            "Normal": "#FFC857",

            "Low": "#49D17D"

        }

        return colors.get(
            self.priority,
            "#FFC857"
        )
