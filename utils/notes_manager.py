import hashlib

from database.database import Database
from database.models import Note


class NotesManager:

    def __init__(self):

        self.database = Database()


    def get_all_notes(self):

        return [
            Note.from_row(row)
            for row in self.database.get_notes()
        ]


    def get_note(self, note_id):

        row = self.database.get_note(note_id)

        return Note.from_row(row) if row else None


    def create_note(self, title="", body="", tags=""):

        return self.database.add_note(title, body, tags)


    def update_note(self, note_id, title, body, tags=""):

        self.database.update_note(note_id, title, body, tags)


    def delete_note(self, note_id):

        self.database.delete_note(note_id)


    def search(self, query):

        query = query.lower().strip()

        if not query:

            return self.get_all_notes()

        return [
            note
            for note in self.get_all_notes()
            if query in note.title.lower()
            or query in note.tags.lower()
            or (not note.locked and query in note.body.lower())
        ]


    # -------------------------
    # LOCK / UNLOCK
    # -------------------------

    @staticmethod
    def _hash_pin(pin):

        return hashlib.sha256(pin.encode("utf-8")).hexdigest()


    def lock_note(self, note_id, pin):

        self.database.set_note_locked(
            note_id,
            True,
            self._hash_pin(pin)
        )


    def unlock_note(self, note_id):

        # Removes the PIN entirely — matches the app-wide pattern of
        # "lock" being a toggle rather than a permanent password.
        self.database.set_note_locked(note_id, False, None)


    def check_pin(self, note, pin):

        return bool(note.pin_hash) and note.pin_hash == self._hash_pin(pin)


    def close(self):

        self.database.close()
