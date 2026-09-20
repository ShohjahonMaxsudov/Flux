from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QLinearGradient


from ui.sidebar import Sidebar

from ui.page_manager import PageManager

from ui.pages.dashboard_page import DashboardPage
from ui.pages.tasks_page import TasksPage
from ui.pages.calendar_page import CalendarPage
from ui.pages.statistics_page import StatisticsPage
from ui.pages.settings_page import SettingsPage
from ui.pages.notes_page import NotesPage

from ui.lock_screen import LockScreen


from animations.aurora import AuroraBackground
from animations.stars import StarField
from animations.sakura import SakuraBackground

from themes.manager import ThemeManager
from utils.settings_manager import SettingsManager



class Flux(QMainWindow):

    def __init__(self):

        super().__init__()

        self.lockScreen = None


        # Load the last theme the user picked before building any
        # widget, so everything constructs with the right colors from
        # frame one instead of always starting on ThemeManager's
        # hardcoded "dark" default and only fixing itself if/when
        # something happens to trigger a theme change afterward.

        startup_settings = SettingsManager()

        ThemeManager.current_name = startup_settings.get_theme()

        startup_settings.close()


        self.setWindowTitle(
            "Flux"
        )


        self.resize(
            1550,
            900
        )


        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )



        self.central = QWidget()


        self.central.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )


        self.setCentralWidget(
            self.central
        )



        # Background
        #
        # Three animated layers live here; apply_background_theme()
        # shows/hides them based on the active theme so the atmosphere
        # actually matches what you switched to instead of staying on
        # the dark aurora regardless of theme.

        self.aurora = AuroraBackground(
            self.central
        )


        self.stars = StarField(
            self.central
        )


        self.sakura = SakuraBackground(
            self.central
        )


        self.aurora.lower()

        self.stars.raise_()

        self.sakura.raise_()



        # Main UI container

        self.uiContainer = QWidget(
            self.central
        )


        self.uiContainer.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )



        layout = QHBoxLayout(
            self.uiContainer
        )


        layout.setContentsMargins(
            22,
            22,
            22,
            22
        )


        layout.setSpacing(
            22
        )



        # Sidebar

        self.sidebar = Sidebar()



        # Pages

        self.pages = PageManager()



        self.dashboardPage = DashboardPage()

        self.tasksPage = TasksPage()

        self.calendarPage = CalendarPage()

        self.notesPage = NotesPage()

        self.statisticsPage = StatisticsPage()

        self.settingsPage = SettingsPage()

        self.settingsPage.nameChanged.connect(
            self.dashboardPage.dashboard.set_user_name
        )



        self.pages.add_page(
            "Dashboard",
            self.dashboardPage
        )


        self.pages.add_page(
            "Tasks",
            self.tasksPage
        )


        self.pages.add_page(
            "Calendar",
            self.calendarPage
        )


        self.pages.add_page(
            "Notes",
            self.notesPage
        )


        self.pages.add_page(
            "Statistics",
            self.statisticsPage
        )


        self.pages.add_page(
            "Settings",
            self.settingsPage
        )



        self.pages.show_page(
            "Dashboard"
        )



        # Sidebar -> Pages

        self.sidebar.filterChanged.connect(
            self.change_page
        )



        layout.addWidget(
            self.sidebar
        )


        layout.addWidget(
            self.pages,
            1
        )



        self.uiContainer.raise_()


        self.apply_background_theme()


        ThemeManager.subscribe(
            self.on_theme_changed
        )



        # Lock screen — shown over everything else at startup if the
        # setting is enabled. Reads the setting fresh via its own
        # SettingsManager/Database connection, same pattern as every
        # other page.

        settings_manager = SettingsManager()

        if settings_manager.get_lock_screen_enabled():

            self.show_lock_screen()

        settings_manager.close()


        self.dashboardPage.dashboard.header.lockClicked.connect(
            self.show_lock_screen
        )


        self.dashboardPage.dashboard.progressChanged.connect(
            self.sidebar.set_progress
        )



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

        self.lockScreen = LockScreen(
            self.central
        )

        self.lockScreen.resize(
            self.central.size()
        )

        self.lockScreen.move(0, 0)

        self.lockScreen.raise_()

        self.lockScreen.show()

        self.lockScreen.unlocked.connect(
            self._on_unlocked
        )



    def _on_unlocked(self):

        self.lockScreen = None

        self.uiContainer.show()



    def apply_background_theme(self):

        theme_name = ThemeManager.current_name


        if theme_name == "sakura":

            self.sakura.show()

            self.sakura.start()

            self.sakura.raise_()

            self.aurora.hide()

            self.aurora.stop()

            self.stars.hide()

            self.stars.stop()


        elif theme_name == "light":

            # Light theme wants a clean, calm surface, not an animated
            # backdrop competing with white glass cards.

            self.sakura.hide()

            self.sakura.stop()

            self.aurora.hide()

            self.aurora.stop()

            self.stars.hide()

            self.stars.stop()


        else:

            self.aurora.show()

            self.aurora.start()

            self.aurora.lower()

            self.stars.show()

            self.stars.start()

            self.stars.raise_()

            self.sakura.hide()

            self.sakura.stop()


        # Whichever background layer is active, the actual UI must stay
        # on top of it. apply_background_theme() raises the active
        # background widget above its sibling backgrounds, which would
        # otherwise also raise it above uiContainer and hide the app
        # behind a fullscreen Sakura/aurora layer.

        self.uiContainer.raise_()


        # Same reasoning applies to the lock screen: raise_() puts a
        # background widget at the very top of the whole sibling stack
        # under self.central, not just above the other backgrounds —
        # so if the lock screen is up when the theme changes (e.g. via
        # its own quick theme switcher), the newly active background
        # would otherwise end up drawn on top of the clock instead of
        # behind it.

        if self.lockScreen is not None:

            self.lockScreen.raise_()



    def on_theme_changed(self, name):

        self.apply_background_theme()

        self.update()


        # Propagate to the widgets that build their own stylesheet once
        # at construction time and otherwise wouldn't know the theme
        # changed underneath them.

        self.sidebar.apply_theme()

        self.dashboardPage.dashboard.refresh_theme()

        self.tasksPage.refresh_theme()

        self.statisticsPage.refresh_theme()

        self.calendarPage.refresh_theme()

        self.notesPage.refresh_theme()

        self.settingsPage.refresh_theme()



    def change_page(
        self,
        name
    ):


        mapping = {

            "All": "Dashboard",

            "Dashboard": "Dashboard",

            "Tasks": "Tasks",

            "Calendar": "Calendar",

            "Notes": "Notes",

            "Statistics": "Statistics",

            "Settings": "Settings",

        }


        if name in mapping:

            self.pages.show_page(
                mapping[name]
            )



    def resizeEvent(
        self,
        event
    ):


        size = self.central.size()


        self.aurora.resize(
            size
        )


        self.stars.resize(
            size
        )


        self.sakura.resize(
            size
        )


        self.uiContainer.resize(
            size
        )


        if self.lockScreen is not None:

            self.lockScreen.resize(
                size
            )


        super().resizeEvent(
            event
        )



    def paintEvent(
        self,
        event
    ):


        theme = ThemeManager.get()


        painter = QPainter(
            self
        )


        gradient = QLinearGradient(
            0,
            0,
            0,
            self.height()
        )


        gradient.setColorAt(
            0,
            QColor(theme.Colors.SECONDARY)
        )


        gradient.setColorAt(
            1,
            QColor(theme.Colors.BACKGROUND)
        )


        painter.fillRect(
            self.rect(),
            gradient
        )