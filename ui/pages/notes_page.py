from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QStackedWidget,
    QScrollArea,
    QInputDialog,
    QMenu
)

from utils.notes_manager import NotesManager
from utils.glass_effects import GlassFrame, RefractiveGlassMixin
from ui.icons import IconGlyph
from themes.manager import ThemeManager


class GlassRoundButton(RefractiveGlassMixin, QPushButton):

    # Same "round + refractive glowing border" treatment already used
    # for the header's icon buttons, reused here for the note editor's
    # back / lock / more controls.

    glass_radius = 18

    def __init__(self, icon_name, size=36):

        super().__init__("")

        self.setFixedSize(size, size)

        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setAlignment(Qt.AlignCenter)

        self.glyph = IconGlyph(icon_name, size=16, color="white", stroke_width=1.8)

        self.glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout.addWidget(self.glyph)


    def apply_glass_theme(self, theme):

        self.setStyleSheet(
            f"""
            QPushButton{{

                background:{theme.Colors.GLASS};

                border:1px solid {theme.Colors.BORDER};

                border-radius:18px;

            }}

            QPushButton:hover{{

                background:{theme.Colors.GLASS_HOVER};

            }}
            """
        )

        self.glyph.setColor(theme.Colors.TEXT)



class NoteCard(GlassFrame):

    glass_radius = 18


    def __init__(self, note, on_open):

        super().__init__()

        self.setObjectName("noteCard")

        self.note = note

        self.on_open = on_open

        self.setCursor(Qt.PointingHandCursor)

        self.setMinimumHeight(100)


        layout = QVBoxLayout(self)

        layout.setContentsMargins(18, 14, 18, 14)

        layout.setSpacing(6)


        topRow = QHBoxLayout()

        self.titleLabel = QLabel(note.title or "Untitled Note")

        topRow.addWidget(self.titleLabel)

        topRow.addStretch()

        if note.locked:

            lockIcon = IconGlyph("lock", size=14, color="white", stroke_width=1.6)

            topRow.addWidget(lockIcon)

        layout.addLayout(topRow)


        self.previewLabel = QLabel(note.preview)

        self.previewLabel.setWordWrap(True)

        layout.addWidget(self.previewLabel)


        self.dateLabel = QLabel(note.updated_at[:16])

        layout.addWidget(self.dateLabel)


        self.apply_theme()


    def apply_theme(self):

        theme = ThemeManager.get()

        self.setStyleSheet(
            f"""
            QFrame#noteCard{{

                background:{theme.Colors.GLASS};

                border:1px solid {theme.Colors.BORDER};

                border-radius:18px;

            }}
            """
        )

        self.titleLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:16px; font-weight:700; background:transparent; border:none;"
        )

        self.previewLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:13px; background:transparent; border:none;"
        )

        self.dateLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:11px; background:transparent; border:none;"
        )


    def mousePressEvent(self, event):

        super().mousePressEvent(event)

        self.on_open(self.note.id)



class NotesPage(QWidget):

    def __init__(self):

        super().__init__()

        self.notes_manager = NotesManager()

        self.current_note_id = None

        self._editor_locked = False

        self.unlocked_ids = set()

        self._save_timer = QTimer(self)

        self._save_timer.setSingleShot(True)

        self._save_timer.timeout.connect(self._save_current_note)


        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)


        self.stack = QStackedWidget()

        root.addWidget(self.stack)


        self.listView = self._build_list_view()

        self.editorView = self._build_editor_view()


        self.stack.addWidget(self.listView)

        self.stack.addWidget(self.editorView)


        self.apply_theme()

        self.load_notes()



    # -------------------------
    # LIST VIEW
    # -------------------------

    def _build_list_view(self):

        view = QWidget()

        layout = QVBoxLayout(view)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(18)


        self.title = QLabel("Notes")

        self.subtitle = QLabel("Your own space to write things down.")

        layout.addWidget(self.title)

        layout.addWidget(self.subtitle)


        toolRow = QHBoxLayout()

        self.searchInput = QLineEdit()

        self.searchInput.setPlaceholderText("Search notes...")

        self.searchInput.textChanged.connect(self.load_notes)

        self.newNoteButton = QPushButton("+  New Note")

        self.newNoteButton.setCursor(Qt.PointingHandCursor)

        self.newNoteButton.clicked.connect(self.create_note)

        toolRow.addWidget(self.searchInput, 1)

        toolRow.addWidget(self.newNoteButton)

        layout.addLayout(toolRow)


        self.notesScroll = QScrollArea()

        self.notesScroll.setWidgetResizable(True)

        self.notesScroll.setFrameShape(QScrollArea.NoFrame)

        self.notesScroll.setStyleSheet(
            "QScrollArea{ background:transparent; border:none; }"
            "QScrollArea > QWidget > QWidget{ background:transparent; }"
        )

        self.notesContent = QWidget()

        self.notesContent.setStyleSheet("background:transparent;")

        self.notesLayout = QVBoxLayout(self.notesContent)

        self.notesLayout.setContentsMargins(0, 0, 0, 0)

        self.notesLayout.setSpacing(12)

        self.notesScroll.setWidget(self.notesContent)

        layout.addWidget(self.notesScroll, 1)


        return view



    # -------------------------
    # EDITOR VIEW
    # -------------------------

    def _build_editor_view(self):

        view = QWidget()

        layout = QVBoxLayout(view)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(16)


        toolbar = QHBoxLayout()

        self.backButton = GlassRoundButton("back")

        self.backButton.clicked.connect(self.show_list)

        toolbar.addWidget(self.backButton)

        toolbar.addStretch()

        self.lockButton = GlassRoundButton("lock")

        self.lockButton.clicked.connect(self.toggle_lock)

        toolbar.addWidget(self.lockButton)

        self.moreButton = GlassRoundButton("more")

        self.moreButton.clicked.connect(self.show_note_menu)

        toolbar.addWidget(self.moreButton)

        layout.addLayout(toolbar)


        self.editorCard = GlassFrame()

        self.editorCard.setObjectName("noteEditorCard")

        self.editorCard.glass_radius = 22

        cardLayout = QVBoxLayout(self.editorCard)

        cardLayout.setContentsMargins(28, 24, 28, 24)

        cardLayout.setSpacing(14)


        self.titleInput = QLineEdit()

        self.titleInput.setPlaceholderText("Title")

        self.titleInput.textChanged.connect(self._schedule_save)

        cardLayout.addWidget(self.titleInput)


        self.contentInput = QTextEdit()

        self.contentInput.setPlaceholderText("Start writing...")

        self.contentInput.textChanged.connect(self._schedule_save)

        cardLayout.addWidget(self.contentInput, 1)


        # -- locked overlay: shown instead of the editable fields when
        # a note is locked and hasn't been unlocked yet this session.

        self.lockedPanel = QWidget()

        lockedLayout = QVBoxLayout(self.lockedPanel)

        lockedLayout.setAlignment(Qt.AlignCenter)

        lockedLayout.setSpacing(12)

        self.lockedIcon = IconGlyph("lock", size=42, color="white", stroke_width=1.6)

        self.lockedLabel = QLabel("This note is locked.")

        self.lockedLabel.setAlignment(Qt.AlignCenter)

        self.viewNoteButton = QPushButton("View Note")

        self.viewNoteButton.setCursor(Qt.PointingHandCursor)

        self.viewNoteButton.clicked.connect(self.attempt_unlock)

        lockedLayout.addWidget(self.lockedIcon, alignment=Qt.AlignCenter)

        lockedLayout.addWidget(self.lockedLabel)

        lockedLayout.addWidget(self.viewNoteButton, alignment=Qt.AlignCenter)

        cardLayout.addWidget(self.lockedPanel, 1)


        layout.addWidget(self.editorCard, 1)


        return view



    def apply_theme(self):

        theme = ThemeManager.get()


        self.title.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:32px; font-weight:800; background:transparent; border:none;"
        )

        self.subtitle.setStyleSheet(
            f"color:{theme.Colors.TEXT_SECONDARY}; font-size:15px; background:transparent; border:none;"
        )

        self.searchInput.setStyleSheet(
            f"""
            QLineEdit{{
                background:{theme.Colors.SURFACE_ALT};
                color:{theme.Colors.TEXT};
                border:1px solid {theme.Colors.BORDER};
                border-radius:12px;
                padding:10px;
            }}
            """
        )

        self.newNoteButton.setStyleSheet(
            f"""
            QPushButton{{
                background:{theme.Colors.PRIMARY};
                color:white;
                border-radius:12px;
                padding:10px 20px;
                font-weight:bold;
            }}
            QPushButton:hover{{
                background:{theme.Colors.BORDER_ACTIVE};
            }}
            """
        )

        for btn in (self.backButton, self.lockButton, self.moreButton):

            btn.apply_glass_theme(theme)


        self.editorCard.setStyleSheet(
            f"""
            QFrame#{self.editorCard.objectName()}{{
                background:{theme.Colors.GLASS};
                border:1px solid {theme.Colors.BORDER};
                border-radius:22px;
            }}
            """
        )

        self.titleInput.setStyleSheet(
            f"""
            QLineEdit{{
                color:{theme.Colors.TEXT};
                background:transparent;
                border:none;
                font-size:24px;
                font-weight:800;
            }}
            """
        )

        self.contentInput.setStyleSheet(
            f"""
            QTextEdit{{
                color:{theme.Colors.TEXT};
                background:transparent;
                border:none;
                font-size:15px;
            }}
            """
        )

        self.lockedIcon.setColor(theme.Colors.TEXT_SECONDARY)

        self.lockedLabel.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:16px; font-weight:600; background:transparent; border:none;"
        )

        self.viewNoteButton.setStyleSheet(
            f"""
            QPushButton{{
                background:{theme.Colors.PRIMARY};
                color:white;
                border-radius:10px;
                padding:8px 18px;
                font-weight:600;
            }}
            """
        )



    def refresh_theme(self):

        self.apply_theme()

        self.load_notes()



    def showEvent(self, event):

        super().showEvent(event)

        if self.stack.currentWidget() is self.listView:

            QTimer.singleShot(0, self.load_notes)



    # -------------------------
    # LIST BEHAVIOR
    # -------------------------

    def load_notes(self):

        while self.notesLayout.count():

            item = self.notesLayout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.hide()

                widget.deleteLater()


        notes = self.notes_manager.search(
            self.searchInput.text()
        )


        theme = ThemeManager.get()


        if not notes:

            empty = QLabel("No notes yet — start your first entry ✎")

            empty.setStyleSheet(
                f"color:{theme.Colors.TEXT_SECONDARY}; font-size:14px; background:transparent; border:none;"
            )

            self.notesLayout.addWidget(empty)


        else:

            for note in notes:

                card = NoteCard(note, self.open_note)

                self.notesLayout.addWidget(card)


        self.notesLayout.addStretch()



    def create_note(self):

        note_id = self.notes_manager.create_note(
            title="",
            body=""
        )

        self.open_note(note_id)



    # -------------------------
    # EDITOR BEHAVIOR
    # -------------------------

    def open_note(self, note_id):

        self._save_current_note()

        self.current_note_id = note_id

        note = self.notes_manager.get_note(note_id)

        if note is None:

            return


        is_locked = note.locked and note_id not in self.unlocked_ids

        self._editor_locked = is_locked

        self.lockedPanel.setVisible(is_locked)

        self.titleInput.setVisible(not is_locked)

        self.contentInput.setVisible(not is_locked)


        self.titleInput.blockSignals(True)

        self.contentInput.blockSignals(True)

        self.titleInput.setText(note.title)

        self.contentInput.setPlainText(note.body)

        self.titleInput.blockSignals(False)

        self.contentInput.blockSignals(False)


        self.lockButton.glyph.name = "lock"

        self.lockButton.glyph.update()


        self.stack.setCurrentWidget(self.editorView)



    def show_list(self):

        self._save_current_note()

        self.stack.setCurrentWidget(self.listView)

        self.load_notes()



    def _schedule_save(self):

        self._save_timer.start(500)



    def _save_current_note(self):

        if self.current_note_id is None:

            return

        if getattr(self, "_editor_locked", False):

            # locked and never unlocked this session — nothing to save
            return

        self.notes_manager.update_note(
            self.current_note_id,
            self.titleInput.text(),
            self.contentInput.toPlainText()
        )



    def toggle_lock(self):

        note = self.notes_manager.get_note(self.current_note_id)

        if note is None:

            return


        if note.locked:

            self.notes_manager.unlock_note(note.id)

            self.unlocked_ids.discard(note.id)


        else:

            self._save_current_note()

            pin, ok = QInputDialog.getText(
                self,
                "Lock Note",
                "Set a PIN for this note:",
                QLineEdit.Password
            )

            if ok and pin.strip():

                self.notes_manager.lock_note(note.id, pin.strip())

                self.unlocked_ids.discard(note.id)

                self.open_note(note.id)

                return


        self.open_note(note.id)



    def attempt_unlock(self):

        note = self.notes_manager.get_note(self.current_note_id)

        if note is None:

            return

        pin, ok = QInputDialog.getText(
            self,
            "Unlock Note",
            "Enter PIN:",
            QLineEdit.Password
        )

        if ok and self.notes_manager.check_pin(note, pin.strip()):

            self.unlocked_ids.add(note.id)

            self.open_note(note.id)



    def show_note_menu(self):

        theme = ThemeManager.get()

        menu = QMenu(self)

        menu.setStyleSheet(
            f"""
            QMenu{{
                background:{theme.Colors.SURFACE};
                color:{theme.Colors.TEXT};
                border:1px solid {theme.Colors.BORDER};
                border-radius:10px;
                padding:6px;
            }}
            QMenu::item{{
                padding:8px 20px;
                border-radius:6px;
            }}
            QMenu::item:selected{{
                background:{theme.Colors.PRIMARY};
                color:white;
            }}
            """
        )

        delete_action = menu.addAction("Delete Note")

        chosen = menu.exec(
            self.moreButton.mapToGlobal(self.moreButton.rect().bottomRight())
        )

        if chosen == delete_action and self.current_note_id is not None:

            self.notes_manager.delete_note(self.current_note_id)

            self.current_note_id = None

            self.show_list()
