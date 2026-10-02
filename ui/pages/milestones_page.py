from datetime import datetime

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from ui.design_system import GradientButton, IconCircle, Metrics, SurfaceCard, clear_layout
from utils.milestone_manager import MilestoneManager


class MilestonesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = MilestoneManager()

        root = QVBoxLayout(self)
        root.setContentsMargins(Metrics.PAGE_X, Metrics.PAGE_Y, Metrics.PAGE_X, Metrics.PAGE_Y)
        root.setSpacing(16)

        self.title = QLabel("Milestones")
        self.title.setObjectName("milestonesTitle")
        self.subtitle = QLabel("Make long-term goals visible, measurable and hard to ignore.")
        self.subtitle.setObjectName("milestonesSubtitle")
        root.addWidget(self.title)
        root.addWidget(self.subtitle)

        stats = QHBoxLayout()
        stats.setSpacing(10)
        self.active_card, self.active_value = self._stat("Active", "star")
        self.done_card, self.done_value = self._stat("Completed", "check")
        self.average_card, self.average_value = self._stat("Average progress", "chart")
        for card in (self.active_card, self.done_card, self.average_card):
            stats.addWidget(card, 1)
        root.addLayout(stats)

        body = QHBoxLayout()
        body.setSpacing(14)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} QScrollArea>QWidget>QWidget{background:transparent;}")
        self.list_host = QWidget()
        self.list_host.setStyleSheet("background:transparent;")
        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(0, 0, 4, 0)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch(1)
        self.scroll.setWidget(self.list_host)
        body.addWidget(self.scroll, 1)

        side = QWidget()
        side.setFixedWidth(320)
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(12)

        self.create_card = SurfaceCard("New Milestone", "Define the finish line first.")
        self.name_input = QLineEdit()
        self.name_input.setObjectName("milestoneInput")
        self.name_input.setPlaceholderText("e.g. Ship Flux v3")
        self.target_input = QSpinBox()
        self.target_input.setObjectName("milestoneInput")
        self.target_input.setRange(1, 100000)
        self.target_input.setValue(100)
        self.target_input.setPrefix("Target  ")
        self.date_input = QDateEdit(QDate.currentDate().addMonths(1))
        self.date_input.setObjectName("milestoneInput")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd MMM yyyy")
        self.add_button = GradientButton("Create Milestone", "plus")
        self.add_button.clicked.connect(self._create)
        self.name_input.returnPressed.connect(self._create)
        self.create_card.body.addWidget(self.name_input)
        self.create_card.body.addWidget(self.target_input)
        self.create_card.body.addWidget(self.date_input)
        self.create_card.body.addWidget(self.add_button)
        side_layout.addWidget(self.create_card)

        self.tip_card = SurfaceCard("How progress works")
        tip = QLabel("Use +10 / −10 for quick updates. Progress is capped at the target, and completed milestones stay visible at the bottom.")
        tip.setObjectName("milestoneHint")
        tip.setWordWrap(True)
        self.tip_card.body.addWidget(tip)
        side_layout.addWidget(self.tip_card)
        side_layout.addStretch(1)

        body.addWidget(side)
        root.addLayout(body, 1)

        self.apply_theme()
        self.load_milestones()

    def _stat(self, label, icon_name):
        frame = QFrame()
        frame.setObjectName("milestoneStat")
        row = QHBoxLayout(frame)
        row.setContentsMargins(14, 11, 14, 11)
        row.setSpacing(10)
        icon = IconCircle(icon_name, 40)
        text = QVBoxLayout()
        text.setSpacing(0)
        value = QLabel("0")
        value.setObjectName("milestoneStatValue")
        caption = QLabel(label)
        caption.setObjectName("milestoneStatCaption")
        text.addWidget(value)
        text.addWidget(caption)
        row.addWidget(icon)
        row.addLayout(text, 1)
        return frame, value

    def _create(self):
        title = self.name_input.text().strip()
        if not title:
            self.name_input.setFocus()
            return
        self.manager.create(
            title=title,
            target=self.target_input.value(),
            due_date=self.date_input.date().toString("yyyy-MM-dd"),
            color=ThemeManager.get().Colors.PRIMARY,
        )
        self.name_input.clear()
        self.target_input.setValue(100)
        self.date_input.setDate(QDate.currentDate().addMonths(1))
        self.load_milestones()

    def _adjust(self, item, delta):
        self.manager.set_progress(item["id"], int(item["progress"]) + delta)
        self.load_milestones()

    def _delete(self, item_id):
        self.manager.delete(item_id)
        self.load_milestones()

    def load_milestones(self):
        items = self.manager.all()
        active = [x for x in items if int(x["progress"]) < int(x["target"])]
        done = [x for x in items if int(x["progress"]) >= int(x["target"])]
        average = round(sum((int(x["progress"]) / max(1, int(x["target"]))) * 100 for x in items) / len(items)) if items else 0
        self.active_value.setText(str(len(active)))
        self.done_value.setText(str(len(done)))
        self.average_value.setText(f"{average}%")

        clear_layout(self.list_layout, keep_stretch=True)
        if not items:
            empty = QLabel("No milestones yet. Create the first one on the right.")
            empty.setObjectName("milestoneEmpty")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.insertWidget(0, empty)
            return

        for item in items:
            self.list_layout.insertWidget(self.list_layout.count() - 1, self._card(item))

    def _card(self, item):
        frame = QFrame()
        frame.setObjectName("milestoneCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        top = QHBoxLayout()
        title = QLabel(item["title"])
        title.setObjectName("milestoneCardTitle")
        target = max(1, int(item["target"]))
        progress = max(0, min(target, int(item["progress"])))
        percent = round(progress / target * 100)
        badge = QLabel("Complete" if progress >= target else f"{progress} / {target}")
        badge.setObjectName("milestoneBadge")
        top.addWidget(title, 1)
        top.addWidget(badge)
        layout.addLayout(top)

        bar = QProgressBar()
        bar.setObjectName("milestoneProgress")
        bar.setRange(0, 100)
        bar.setValue(percent)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        layout.addWidget(bar)

        bottom = QHBoxLayout()
        due = item.get("due_date") or ""
        due_text = "No due date"
        if due:
            try:
                due_text = "Due " + datetime.strptime(due, "%Y-%m-%d").strftime("%b %d, %Y")
            except ValueError:
                due_text = "Due " + due
        due_label = QLabel(due_text)
        due_label.setObjectName("milestoneDue")
        minus = QPushButton("−10")
        plus = QPushButton("+10")
        delete = QPushButton("Delete")
        for button in (minus, plus, delete):
            button.setObjectName("milestoneSmallButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete.setProperty("danger", True)
        minus.clicked.connect(lambda _checked=False, x=item: self._adjust(x, -10))
        plus.clicked.connect(lambda _checked=False, x=item: self._adjust(x, 10))
        delete.clicked.connect(lambda _checked=False, item_id=item["id"]: self._delete(item_id))
        bottom.addWidget(due_label, 1)
        bottom.addWidget(minus)
        bottom.addWidget(plus)
        bottom.addWidget(delete)
        layout.addLayout(bottom)
        return frame

    def apply_theme(self):
        c = ThemeManager.get().Colors
        self.create_card.apply_theme()
        self.tip_card.apply_theme()
        self.add_button.apply_theme()
        self.setStyleSheet(
            f"""
            QLabel#milestonesTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:28px; font-weight:800; }}
            QLabel#milestonesSubtitle {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:12px; }}
            QFrame#milestoneStat, QFrame#milestoneCard {{ background:{c.SURFACE}; border:1px solid {c.BORDER}; border-radius:14px; }}
            QLabel#milestoneStatValue {{ color:{c.TEXT}; background:transparent; border:none; font-size:20px; font-weight:800; }}
            QLabel#milestoneStatCaption, QLabel#milestoneDue, QLabel#milestoneHint {{ color:{c.TEXT_SECONDARY}; background:transparent; border:none; font-size:10px; }}
            QLineEdit#milestoneInput, QSpinBox#milestoneInput, QDateEdit#milestoneInput {{ color:{c.TEXT}; background:{c.SURFACE_ALT}; border:1px solid {c.BORDER}; border-radius:10px; padding:9px 10px; }}
            QLineEdit#milestoneInput:focus, QSpinBox#milestoneInput:focus, QDateEdit#milestoneInput:focus {{ border-color:{c.BORDER_ACTIVE}; }}
            QLabel#milestoneCardTitle {{ color:{c.TEXT}; background:transparent; border:none; font-size:14px; font-weight:700; }}
            QLabel#milestoneBadge {{ color:{c.PRIMARY_LIGHT}; background:rgba(79,103,244,0.14); border:1px solid rgba(100,135,255,0.20); border-radius:9px; padding:4px 8px; font-size:10px; }}
            QProgressBar#milestoneProgress {{ background:#202A39; border:none; border-radius:4px; }}
            QProgressBar#milestoneProgress::chunk {{ background:{c.PRIMARY_LIGHT}; border-radius:4px; }}
            QPushButton#milestoneSmallButton {{ color:{c.TEXT_SECONDARY}; background:{c.SURFACE_ALT}; border:1px solid {c.BORDER}; border-radius:8px; padding:6px 9px; font-size:10px; }}
            QPushButton#milestoneSmallButton:hover {{ color:{c.TEXT}; border-color:{c.BORDER_ACTIVE}; }}
            QPushButton#milestoneSmallButton[danger="true"]:hover {{ color:{c.ERROR}; border-color:{c.ERROR}; }}
            QLabel#milestoneEmpty {{ color:{c.TEXT_SECONDARY}; background:{c.SURFACE}; border:1px solid {c.BORDER}; border-radius:14px; padding:46px; font-size:11px; }}
            """
        )

    def refresh_theme(self):
        self.apply_theme()
        self.load_milestones()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_milestones()
