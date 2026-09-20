import sys
import os
import shutil
import sqlite3
from pathlib import Path


def _app_data_dir():
    """
    Where Flux keeps its database once it's running as a packaged app
    (PyInstaller build) rather than from source.

    A frozen app can end up installed somewhere read-only (Program
    Files) and, if built --onefile, actually runs from a temp folder
    that gets wiped after every session. So `Path(__file__).parent`
    - fine for `python main.py` - is not a safe place to keep a
    persistent SQLite file once the app is packaged. Every OS has its
    own writable, per-user folder for exactly this.
    """

    app_name = "Flux"

    if sys.platform == "win32":
        base = (
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or str(Path.home())
        )
        return Path(base) / app_name

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / app_name

    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / app_name


class Database:


    def __init__(self):

        self.db_path = self._resolve_db_path()

        self.connection = None

        self.connect()

        self.create_tables()

        self.upgrade_database()


    def _resolve_db_path(self):

        # Running from source (`python main.py`): unchanged behavior,
        # a flux.db right next to this file.
        if not getattr(sys, "frozen", False):
            return Path(__file__).parent / "flux.db"

        # Running as a packaged app: use a per-user data folder that
        # is guaranteed writable and persists between runs/updates.
        data_dir = _app_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)

        db_path = data_dir / "flux.db"

        # One-time migration: if a dev flux.db ended up bundled next
        # to the source and this is the first run, carry its data
        # over instead of starting empty.
        if not db_path.exists():
            bundled = Path(__file__).parent / "flux.db"
            if bundled.exists():
                try:
                    shutil.copy2(bundled, db_path)
                except OSError:
                    pass

        return db_path



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
                "INTEGER DEFAULT 0"

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

            SET completed = ?

            WHERE id = ?

            """,

            (
                1 if completed else 0,
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
