import sqlite3
from pathlib import Path
from datetime import datetime



class Database:


    def __init__(self):

        self.db_path = (
            Path(__file__).parent / "flux.db"
        )

        self.connection = None

        self.connect()

        self.create_tables()

        self.upgrade_database()



    def connect(self):

        self.connection = sqlite3.connect(
            self.db_path
        )

        self.connection.row_factory = sqlite3.Row



    def create_tables(self):

        cursor = self.connection.cursor()


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            time TEXT,

            task_date TEXT,

            priority TEXT DEFAULT 'Normal',

            category TEXT DEFAULT 'General',

            description TEXT DEFAULT '',

            color TEXT DEFAULT '#5A7DFF',

            reminder TEXT DEFAULT 'None',

            repeat TEXT DEFAULT 'Never',

            important INTEGER DEFAULT 0,

            completed INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)



        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE NOT NULL,

            color TEXT

        )
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL DEFAULT '',

            body TEXT NOT NULL DEFAULT '',

            tags TEXT NOT NULL DEFAULT '',

            locked INTEGER NOT NULL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            key TEXT PRIMARY KEY,

            value TEXT

        )
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            color TEXT DEFAULT '#5A7DFF',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (

            habit_id INTEGER NOT NULL,

            day TEXT NOT NULL,

            completed INTEGER NOT NULL DEFAULT 0,

            PRIMARY KEY (habit_id, day),

            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE

        )
        """)


        self.connection.commit()



    def get_setting(self, key, default=None):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,)
        )

        row = cursor.fetchone()

        return row["value"] if row else default



    def set_setting(self, key, value):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value)
        )

        self.connection.commit()



    # -------------------------
    # NOTES
    # -------------------------

    def add_note(self, title="", body="", tags=""):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO notes (title, body, tags)
            VALUES (?, ?, ?)
            """,
            (title, body, tags)
        )

        self.connection.commit()

        return cursor.lastrowid


    # -------------------------
    # FOCUS SESSIONS
    # -------------------------

    def add_focus_session(self, minutes, session_date):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO focus_sessions (minutes, session_date)
            VALUES (?, ?)
            """,
            (minutes, session_date)
        )

        self.connection.commit()

        return cursor.lastrowid


    def get_focus_sessions(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT * FROM focus_sessions ORDER BY id DESC"
        )

        return cursor.fetchall()


    def get_notes(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT * FROM notes ORDER BY updated_at DESC"
        )

        return cursor.fetchall()


    def get_note(self, note_id):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,)
        )

        return cursor.fetchone()


    def update_note(self, note_id, title, body, tags):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            UPDATE notes
            SET title = ?, body = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, body, tags, note_id)
        )

        self.connection.commit()


    def set_note_locked(self, note_id, locked, pin_hash=None):

        cursor = self.connection.cursor()

        cursor.execute(
            "UPDATE notes SET locked = ?, pin_hash = ? WHERE id = ?",
            (1 if locked else 0, pin_hash, note_id)
        )

        self.connection.commit()


    def delete_note(self, note_id):

        cursor = self.connection.cursor()

        cursor.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,)
        )

        self.connection.commit()



    def upgrade_database(self):

        cursor = self.connection.cursor()


        cursor.execute(
            "PRAGMA table_info(tasks)"
        )


        columns = [

            row[1]

            for row in cursor.fetchall()

        ]



        new_columns = {

            "task_date":
                "TEXT",

            "description":
                "TEXT DEFAULT ''",

            "color":
                "TEXT DEFAULT '#5A7DFF'",

            "reminder":
                "TEXT DEFAULT 'None'",

            "repeat":
                "TEXT DEFAULT 'Never'",

            "important":
                "INTEGER DEFAULT 0",

            "completed_at":
                "TIMESTAMP"

        }



        for name, data_type in new_columns.items():

            if name not in columns:

                cursor.execute(
                    f"""
                    ALTER TABLE tasks
                    ADD COLUMN {name} {data_type}
                    """
                )



        cursor.execute(
            "CREATE TABLE IF NOT EXISTS focus_sessions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "minutes INTEGER NOT NULL, "
            "session_date TEXT NOT NULL, "
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )


        cursor.execute(
            "PRAGMA table_info(notes)"
        )

        note_columns = [
            row[1]
            for row in cursor.fetchall()
        ]

        if "pin_hash" not in note_columns:

            cursor.execute(
                "ALTER TABLE notes ADD COLUMN pin_hash TEXT"
            )


        self.connection.commit()



    # -------------------------
    # HABITS
    # -------------------------


    def add_habit(self, name, color="#5A7DFF"):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO habits (name, color)
            VALUES (?, ?)
            """,
            (
                (name or "").strip(),
                color
            )
        )

        self.connection.commit()

        return cursor.lastrowid


    def get_habits(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM habits
            ORDER BY id ASC
            """
        )

        return cursor.fetchall()


    def delete_habit(self, habit_id):

        cursor = self.connection.cursor()

        cursor.execute(
            "DELETE FROM habit_logs WHERE habit_id = ?",
            (habit_id,)
        )

        cursor.execute(
            "DELETE FROM habits WHERE id = ?",
            (habit_id,)
        )

        self.connection.commit()


    def get_habit_day(self, habit_id, day):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT completed
            FROM habit_logs
            WHERE habit_id = ? AND day = ?
            """,
            (
                habit_id,
                day
            )
        )

        row = cursor.fetchone()

        return bool(
            row["completed"]
            if row
            else 0
        )


    def set_habit_day(self, habit_id, day, completed):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO habit_logs
            (
                habit_id,
                day,
                completed
            )
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, day)
            DO UPDATE SET completed = excluded.completed
            """,
            (
                habit_id,
                day,
                1 if completed else 0
            )
        )

        self.connection.commit()


    def get_habit_logs(self, habit_id=None):

        cursor = self.connection.cursor()

        if habit_id is None:

            cursor.execute(
                """
                SELECT *
                FROM habit_logs
                WHERE completed = 1
                ORDER BY day ASC
                """
            )

        else:

            cursor.execute(
                """
                SELECT *
                FROM habit_logs
                WHERE habit_id = ? AND completed = 1
                ORDER BY day ASC
                """,
                (habit_id,)
            )

        return cursor.fetchall()



    # -------------------------
    # TASKS
    # -------------------------


    def add_task(
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


        cursor = self.connection.cursor()


        cursor.execute(
        """
        INSERT INTO tasks

        (
            title,
            time,
            task_date,
            priority,
            category,
            description,
            color,
            reminder,
            repeat,
            important
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,

        (
            title,
            time,
            task_date,
            priority,
            category,
            description,
            color,
            reminder,
            repeat,
            1 if important else 0
        )

        )


        self.connection.commit()


        return cursor.lastrowid



    def get_tasks(self):

        cursor = self.connection.cursor()


        cursor.execute(
            """
            SELECT *
            FROM tasks
            ORDER BY id DESC
            """
        )


        return cursor.fetchall()



    def update_task(
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

        # NOTE: this method did not exist before — TaskManager.edit_task()
        # was calling it anyway, so saving an edited task raised
        # AttributeError and crashed the dialog. Every field the Edit
        # Task dialog collects is written back here, not just the four
        # that used to make it through.

        cursor = self.connection.cursor()


        cursor.execute(
            """
            UPDATE tasks

            SET title = ?,
                time = ?,
                task_date = ?,
                priority = ?,
                category = ?,
                description = ?,
                color = ?,
                reminder = ?,
                repeat = ?,
                important = ?

            WHERE id = ?
            """,

            (
                title,
                time,
                task_date,
                priority,
                category,
                description,
                color,
                reminder,
                repeat,
                1 if important else 0,
                task_id
            )

        )


        self.connection.commit()



    def update_task_status(
        self,
        task_id,
        completed
    ):


        cursor = self.connection.cursor()


        cursor.execute(
            """
            UPDATE tasks

            SET completed = ?,
                completed_at = ?

            WHERE id = ?

            """,

            (
                1 if completed else 0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed else None,
                task_id
            )

        )


        self.connection.commit()



    def delete_task(
        self,
        task_id
    ):


        cursor = self.connection.cursor()


        cursor.execute(
            """
            DELETE FROM tasks

            WHERE id = ?

            """,

            (task_id,)
        )


        self.connection.commit()



    def close(self):

        if self.connection:

            self.connection.close()
