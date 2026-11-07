from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QLabel,
    QGraphicsOpacityEffect,
    QApplication,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QEvent
from PySide6.QtGui import QPainter, QColor, QLinearGradient

from ui.sidebar import Sidebar
from ui.page_manager import PageManager
from ui.pages.dashboard_page import DashboardPage
from ui.pages.tasks_page import TasksPage
from ui.pages.calendar_page import CalendarPage
from ui.pages.statistics_page import StatisticsPage
from ui.pages.settings_page import SettingsPage
from ui.pages.focus_page import FocusPage
from ui.toast import ToastHost
from ui.pages.notes_page import NotesPage
from ui.pages.habits_page import HabitsPage
from ui.lock_screen import LockScreen
from animations.aurora import AuroraBackground
from animations.stars import StarField
from animations.sakura import SakuraBackground
from animations.astro import AstroBackground
from animations.synthwave import SynthwaveBackground
from themes.manager import ThemeManager
from utils.settings_manager import SettingsManager


class Flux(QMainWindow):
    def __init__(self):
        super().__init__()
        self._theme_fade = None
        self.lockScreen = None
        startup_settings = SettingsManager()
        ThemeManager.current_name = startup_settings.get_theme()
        self.reduce_motion = startup_settings.get("reduce_motion", "0") == "1"
        startup_settings.close()
        self.setWindowTitle("Flux")
        self.resize(1550, 900)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.central = QWidget()
        self.central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(self.central)
        self.aurora = AuroraBackground(self.central)
        self.stars = StarField(self.central)
        self.sakura = SakuraBackground(self.central)
        self.astro = AstroBackground(self.central)
        self.synthwave = SynthwaveBackground(self.central)
        self.aurora.lower()
        self.stars.raise_()
        self.sakura.raise_()
        self.uiContainer = QWidget(self.central)
        self.uiContainer.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QHBoxLayout(self.uiContainer)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(22)
        self.sidebar = Sidebar()
        self.pages = PageManager()
        self.dashboardPage = DashboardPage()
        self.tasksPage = TasksPage()
        self.habitsPage = HabitsPage()
        self.calendarPage = CalendarPage()
        self.notesPage = NotesPage()
        self.statisticsPage = StatisticsPage()
        self.settingsPage = SettingsPage()
        self.focusPage = FocusPage()
        self.settingsPage.nameChanged.connect(self.dashboardPage.dashboard.set_user_name)
        self.pages.add_page("Dashboard", self.dashboardPage)
        self.pages.add_page("Tasks", self.tasksPage)
        self.pages.add_page("Habits", self.habitsPage)
        self.pages.add_page("Focus", self.focusPage)
        self.pages.add_page("Calendar", self.calendarPage)
        self.pages.add_page("Notes", self.notesPage)
        self.pages.add_page("Statistics", self.statisticsPage)
        self.pages.add_page("Settings", self.settingsPage)
        self.pages.show_page("Dashboard")
        self.sidebar.filterChanged.connect(self.change_page)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages, 1)
        self.uiContainer.raise_()
        self.toastHost = ToastHost(self.central)
        self.settingsPage.reduceMotionChanged.connect(self.set_reduce_motion)
        self.settingsPage.weeklyGoalChanged.connect(
            lambda _value: self.dashboardPage.dashboard.update_statistics()
        )
        self.apply_background_theme()
        app = QApplication.instance()

        if app is not None:
            app.applicationStateChanged.connect(self._on_application_state_changed)

        ThemeManager.subscribe_before(self.begin_theme_fade)
        ThemeManager.subscribe(self.on_theme_changed)
        ThemeManager.subscribe_style(self.on_theme_style_changed)
        settings_manager = SettingsManager()

        if settings_manager.get_lock_screen_enabled():
            self.show_lock_screen()

        settings_manager.close()
        self.dashboardPage.dashboard.header.lockClicked.connect(self.show_lock_screen)
        self.dashboardPage.dashboard.progressChanged.connect(self.sidebar.set_progress)

    def show_lock_screen(self):
        if self.lockScreen is not None:
            return

        # Hide the actual app while locked rather than just dimming
        # it — a translucent scrim over an already-dark theme barely
        # obscures anything. Real lock screens don't render the
        # desktop underneath at all; only the wallpaper (here: the
        # theme's animated background, already a sibling beneath
        # uiContainer) shows behind the clock.
        self.uiContainer.hide()
        self.lockScreen = LockScreen(self.central)
        self.lockScreen.resize(self.central.size())
        self.lockScreen.move(0, 0)
        self.lockScreen.raise_()
        self.lockScreen.show()
        self.lockScreen.unlocked.connect(self._on_unlocked)

    def _on_unlocked(self):
        self.lockScreen = None
        self.uiContainer.show()

    def apply_background_theme(self):
        atmosphere = ThemeManager.atmosphere()
        kind = atmosphere.KIND
        animations_allowed = not self.reduce_motion and self.isVisible() and not self.isMinimized() and QApplication.applicationState() == Qt.ApplicationState.ApplicationActive
        scenes = {"sakura": self.sakura, "astro": self.astro, "synthwave": self.synthwave}

        for scene_kind, scene in scenes.items():
            if scene_kind == kind:
                scene.show()

                if animations_allowed:
                    scene.start()
                else:
                    scene.stop()

                scene.lower()
            else:
                scene.hide()
                scene.stop()

        if kind == "aurora":
            self.aurora.configure(atmosphere)
            self.aurora.show()

            if animations_allowed:
                self.aurora.start()
            else:
                self.aurora.stop()

            self.aurora.lower()
        else:
            self.aurora.hide()
            self.aurora.stop()

        wants_particles = kind in (
            "aurora", "astro", "synthwave"
        ) and atmosphere.PARTICLES != "none"

        if wants_particles:
            self.stars.configure(atmosphere)
            self.stars.show()

            if animations_allowed:
                self.stars.start()
            else:
                self.stars.stop()

            self.stars.raise_()
        else:
            self.stars.hide()
            self.stars.stop()

        if kind == "sakura":
            self.sakura.raise_()

        if self.reduce_motion:
            for widget in (self.aurora, self.stars, self.sakura, self.astro, self.synthwave):
                widget.stop()

        self.uiContainer.raise_()

        if self._theme_fade is not None:
            self._theme_fade["overlay"].raise_()

        if self.lockScreen is not None:
            self.lockScreen.raise_()

        self.toastHost.raise_()

    def set_reduce_motion(self, enabled):
        self.reduce_motion = enabled
        self.apply_background_theme()

    def begin_theme_fade(self, old_name, new_name):
        # Called *before* the theme switches. Grab the current look into a
        # snapshot and lay it over the window; everything then restyles
        # underneath it in the same event-loop turn (so the new look is
        # never visible un-faded), and the snapshot dissolves away.
        if not self.isVisible() or self.central.width() < 10:
            return

        if self._theme_fade is not None:
            self._theme_fade["overlay"].deleteLater()
            self._theme_fade["animation"].stop()
            self._theme_fade = None

        overlay = QLabel(self.central)
        overlay.setPixmap(self.central.grab())
        overlay.setGeometry(self.central.rect())
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        effect = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(effect)
        overlay.show()
        overlay.raise_()
        animation = QPropertyAnimation(effect, b"opacity", overlay)
        animation.setDuration(520)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.InOutCubic)

        def finish():
            overlay.deleteLater()

            if self._theme_fade and self._theme_fade["overlay"] is overlay:
                self._theme_fade = None

        animation.finished.connect(finish)
        self._theme_fade = {"overlay": overlay, "animation": animation}

        # Start on the next loop turn: the restyle that follows this call
        # blocks the event loop for a moment, and starting now would eat
        # the first part of the fade.
        QTimer.singleShot(0, animation.start)

    def on_theme_changed(self, name):
        # Re-apply the app-wide stylesheet here, once, so every way of
        # switching themes (header, Settings, lock screen) gets it.
        self._restyle_everything()

    def on_theme_style_changed(self, name):
        # The Custom theme's color/glow being nudged live, not a switch to a
        # different theme: same repaint, but no cross-fade overlay (it reads as
        # responsive tuning rather than a jarring transition).
        self._restyle_everything()

    def _restyle_everything(self):
        app = QApplication.instance()

        if app:
            app.setStyleSheet(ThemeManager.stylesheet())

        self.apply_background_theme()
        self.update()
        self.sidebar.apply_theme()
        self.dashboardPage.dashboard.refresh_theme()
        self.tasksPage.refresh_theme()
        self.habitsPage.refresh_theme()
        self.focusPage.refresh_theme()
        self.statisticsPage.refresh_theme()
        self.calendarPage.refresh_theme()
        self.notesPage.refresh_theme()
        self.settingsPage.refresh_theme()

    def change_page(self, name):
        mapping = {
            "All": "Dashboard",
            "Dashboard": "Dashboard",
            "Tasks": "Tasks",
            "Habits": "Habits",
            "Focus": "Focus",
            "Calendar": "Calendar",
            "Notes": "Notes",
            "Statistics": "Statistics",
            "Settings": "Settings",
        }

        if name in mapping:
            self.pages.show_page(mapping[name])

    def _stop_background_animations(self):
        for widget in (self.aurora, self.stars, self.sakura, self.astro, self.synthwave):
            widget.stop()

    def _sync_animation_activity(self):
        if self.reduce_motion or not self.isVisible() or self.isMinimized() or QApplication.applicationState() != Qt.ApplicationState.ApplicationActive:
            self._stop_background_animations()
            return

        self.apply_background_theme()

    def _on_application_state_changed(self, _state):
        QTimer.singleShot(0, self._sync_animation_activity)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._sync_animation_activity)

    def hideEvent(self, event):
        self._stop_background_animations()
        super().hideEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)

        if event.type() == QEvent.Type.WindowStateChange:
            QTimer.singleShot(0, self._sync_animation_activity)

    def resizeEvent(self, event):
        size = self.central.size()
        self.aurora.resize(size)
        self.stars.resize(size)
        self.sakura.resize(size)
        self.astro.resize(size)
        self.synthwave.resize(size)
        self.uiContainer.resize(size)

        if self.lockScreen is not None:
            self.lockScreen.resize(size)

        self.toastHost.reposition()
        super().resizeEvent(event)

    def paintEvent(self, event):
        theme = ThemeManager.get()
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(theme.Colors.SECONDARY))
        gradient.setColorAt(1, QColor(theme.Colors.BACKGROUND))
        painter.fillRect(self.rect(), gradient)
