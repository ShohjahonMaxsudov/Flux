import os

from PySide6.QtGui import QColor, QLinearGradient, QPainter, QRadialGradient
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QMainWindow, QWidget

from themes.manager import ThemeManager
from ui.lock_screen import LockScreen
from ui.page_manager import PageManager
from ui.pages.calendar_page import CalendarPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.focus_page import FocusPage
from ui.pages.milestones_page import MilestonesPage
from ui.pages.notes_page import NotesPage
from ui.pages.settings_page import SettingsPage
from ui.pages.statistics_page import StatisticsPage
from ui.pages.tasks_page import TasksPage
from ui.sidebar import Sidebar
from ui.toast import ToastHost
from utils.settings_manager import SettingsManager


class Flux(QMainWindow):
    def __init__(self):
        super().__init__()

        self.lockScreen = None
        ThemeManager.current_name = "midnight"

        self.setWindowTitle("Flux")
        self.resize(1480, 900)
        self.setMinimumSize(1180, 720)

        self.central = QWidget()
        self.central.setObjectName("fluxRoot")
        self.setCentralWidget(self.central)

        outer = QHBoxLayout(self.central)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(0)

        self.shell = QFrame()
        self.shell.setObjectName("appShell")

        shell_layout = QHBoxLayout(self.shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.filterChanged.connect(self.change_page)

        self.pages = PageManager()
        self.pages.setContentsMargins(0, 0, 0, 0)

        self.dashboardPage = DashboardPage()
        self.tasksPage = TasksPage()
        self.calendarPage = CalendarPage()
        self.notesPage = NotesPage()
        self.focusPage = FocusPage()
        self.statisticsPage = StatisticsPage()
        self.milestonesPage = MilestonesPage()
        self.settingsPage = SettingsPage()

        for name, page in (
            ("Dashboard", self.dashboardPage),
            ("Tasks", self.tasksPage),
            ("Calendar", self.calendarPage),
            ("Notes", self.notesPage),
            ("Focus", self.focusPage),
            ("Statistics", self.statisticsPage),
            ("Milestones", self.milestonesPage),
            ("Settings", self.settingsPage),
        ):
            self.pages.add_page(name, page)

        shell_layout.addWidget(self.sidebar)
        shell_layout.addWidget(self.pages, 1)
        outer.addWidget(self.shell, 1)

        self.toastHost = ToastHost(self.central)

        self.dashboardPage.dashboard.navigateRequested.connect(
            self.change_page
        )

        if hasattr(self.settingsPage, "nameChanged"):
            self.settingsPage.nameChanged.connect(
                self.dashboardPage.dashboard.set_user_name
            )

        if hasattr(self.settingsPage, "weeklyGoalChanged"):
            self.settingsPage.weeklyGoalChanged.connect(
                lambda _value: self.dashboardPage.dashboard.refresh_data()
            )

        self.pages.show_page("Dashboard")
        self.sidebar.set_active("Dashboard")
        self.apply_theme()

        if os.environ.get("FLUX_PREVIEW") != "1":
            settings = SettingsManager()
            if settings.get_lock_screen_enabled():
                self.show_lock_screen()
            settings.close()

    def change_page(self, name):
        if name not in self.pages.pages:
            return

        self.pages.show_page(name)
        self.sidebar.set_active(name)

        page = self.pages.pages[name]
        if hasattr(page, "refresh_theme"):
            page.refresh_theme()

        if name == "Dashboard":
            self.dashboardPage.dashboard.refresh_data()
        elif name == "Tasks":
            self.tasksPage.load_tasks()
        elif name == "Milestones":
            self.milestonesPage.load_milestones()

    def apply_theme(self):
        c = ThemeManager.get().Colors
        app = QApplication.instance()
        if app:
            app.setStyleSheet(ThemeManager.stylesheet())

        self.shell.setStyleSheet(
            f"""
            QFrame#appShell {{
                background:{c.BACKGROUND};
                border:1px solid rgba(125,150,190,0.20);
                border-radius:18px;
            }}
            """
        )
        self.sidebar.apply_theme()
        self.update()

    def set_reduce_motion(self, _enabled):
        pass

    def show_lock_screen(self):
        if self.lockScreen is not None:
            return

        self.shell.hide()
        self.lockScreen = LockScreen(self.central)
        self.lockScreen.setGeometry(self.central.rect())
        self.lockScreen.raise_()
        self.lockScreen.show()
        self.lockScreen.unlocked.connect(self._on_unlocked)

    def _on_unlocked(self):
        if self.lockScreen is not None:
            self.lockScreen.deleteLater()
        self.lockScreen = None
        self.shell.show()

    def resizeEvent(self, event):
        if self.lockScreen is not None:
            self.lockScreen.setGeometry(self.central.rect())
        self.toastHost.reposition()
        super().resizeEvent(event)

    def paintEvent(self, event):
        c = ThemeManager.get().Colors
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        base = QLinearGradient(0, 0, self.width(), self.height())
        base.setColorAt(0.00, QColor("#12223D"))
        base.setColorAt(0.22, QColor(c.BACKGROUND))
        base.setColorAt(0.74, QColor(c.BACKGROUND))
        base.setColorAt(1.00, QColor("#12213C"))
        painter.fillRect(self.rect(), base)

        left_glow = QRadialGradient(
            self.width() * 0.04,
            self.height() * 0.42,
            self.width() * 0.34
        )
        left_glow.setColorAt(0.0, QColor(69, 107, 255, 88))
        left_glow.setColorAt(0.45, QColor(60, 96, 230, 34))
        left_glow.setColorAt(1.0, QColor(30, 50, 90, 0))
        painter.fillRect(self.rect(), left_glow)

        right_glow = QRadialGradient(
            self.width() * 0.96,
            self.height() * 0.86,
            self.width() * 0.36
        )
        right_glow.setColorAt(0.0, QColor(66, 101, 238, 72))
        right_glow.setColorAt(0.45, QColor(55, 83, 190, 28))
        right_glow.setColorAt(1.0, QColor(20, 35, 65, 0))
        painter.fillRect(self.rect(), right_glow)
