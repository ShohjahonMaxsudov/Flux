from datetime import datetime

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    QRectF,
    Signal
)

from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QFont,
    QFontMetrics,
    QPen,
    QLinearGradient
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGraphicsOpacityEffect
)

from themes.manager import ThemeManager
from utils.settings_manager import SettingsManager
from ui.icons import IconGlyph


class LockScreen(QWidget):

    # A startup lock screen in the iPad/Windows spirit. The clock
    # specifically follows a reference screenshot: a plain slim date
    # label, then a big glowing, rounded-bold clock beneath it (set in
    # the bundled "Fredoka One" font — no system font has that chunky
    # a look), colored from the active theme's accent rather than
    # plain white. Over the app's own animated background (already
    # painted behind this widget, dimmed by a scrim so text stays
    # legible). Dismissed by dragging up, a plain click, or any key
    # press. A small quick theme switcher at the bottom lets you
    # change themes without having to unlock first.

    unlocked = Signal()

    DRAG_DISMISS_THRESHOLD = 120


    def __init__(self, parent=None):

        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFocusPolicy(
            Qt.StrongFocus
        )

        self.setCursor(
            Qt.PointingHandCursor
        )


        self._dragging = False

        self._drag_start_global_y = 0

        self._drag_start_widget_y = 0

        self._dismissed = False


        self.settings_manager = SettingsManager()

        user_name = self.settings_manager.get_user_name()


        self._date_text = ""

        self._time_text = "00:00"


        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 60, 0, 40)

        layout.setAlignment(Qt.AlignHCenter)


        # -- date + clock reserve their space here as a plain spacer;
        # the actual text is hand-painted in paintEvent() because the
        # cutout/blend look (background bleeding through translucent
        # digits, a crisp light rim, subtle engraved depth) needs real
        # QPainter compositing — a QLabel stylesheet can't do any of
        # that.

        self.clockArea = QWidget()

        self.clockArea.setFixedHeight(190)

        self.clockArea.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )


        # -- avatar + name, in place of a static "FLUX" wordmark —
        # there's no profile photo, so a circular initial badge stands
        # in for it, same idea as the macOS account picture.

        initial = (user_name[:1] or "F").upper()

        self.avatar = QLabel(initial)

        self.avatar.setAlignment(Qt.AlignCenter)

        self.avatar.setFixedSize(72, 72)

        self.avatar.setStyleSheet(
            "background:rgba(255,255,255,0.16); "
            "border:2px solid rgba(255,255,255,0.55); "
            "border-radius:36px; color:white; "
            "font-size:28px; font-weight:600;"
        )


        self.nameLabel = QLabel(user_name or "Flux")

        self.nameLabel.setAlignment(Qt.AlignCenter)

        self.nameLabel.setStyleSheet(
            "color:white; font-size:17px; font-weight:600; "
            "background:transparent;"
        )


        self.hint = QLabel("⌃\nClick, press any key, or swipe up")

        self.hint.setAlignment(Qt.AlignCenter)

        self.hint.setStyleSheet(
            "color:rgba(255,255,255,0.75); font-size:14px; "
            "background:transparent;"
        )


        # -- quick theme switcher

        themeRow = QHBoxLayout()

        themeRow.setSpacing(14)

        themeRow.setAlignment(Qt.AlignCenter)

        self.themeButtons = {}

        for key in ThemeManager.names():

            icon_name = ThemeManager.icon(key)

            btn = QPushButton("")

            btn.setFixedSize(40, 40)

            btn.setCursor(Qt.PointingHandCursor)

            btn.setCheckable(True)

            btn.setToolTip(ThemeManager.label(key))

            btnLayout = QHBoxLayout(btn)

            btnLayout.setContentsMargins(0, 0, 0, 0)

            btnLayout.setAlignment(Qt.AlignCenter)

            glyph = IconGlyph(icon_name, size=18, color="white", stroke_width=1.8)

            glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            btnLayout.addWidget(glyph)

            btn.clicked.connect(
                lambda checked, k=key: self.select_theme(k)
            )

            self.themeButtons[key] = btn

            themeRow.addWidget(btn)

        self.sync_theme_buttons()



        layout.addStretch(1)

        layout.addWidget(self.clockArea)

        layout.addStretch(6)

        layout.addWidget(
            self.avatar,
            alignment=Qt.AlignCenter
        )

        layout.addSpacing(10)

        layout.addWidget(self.nameLabel)

        layout.addStretch(1)

        layout.addWidget(self.hint)

        layout.addSpacing(24)

        layout.addLayout(themeRow)

        layout.addSpacing(12)


        self.apply_theme_button_styles()


        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_clock
        )

        self.timer.start(1000)

        self.update_clock()


        self._hint_effect = QGraphicsOpacityEffect(self.hint)

        self.hint.setGraphicsEffect(
            self._hint_effect
        )

        self._hint_pulse = QPropertyAnimation(
            self._hint_effect,
            b"opacity"
        )

        self._hint_pulse.setDuration(1600)

        self._hint_pulse.setKeyValueAt(0.0, 1.0)

        self._hint_pulse.setKeyValueAt(0.5, 0.35)

        self._hint_pulse.setKeyValueAt(1.0, 1.0)

        self._hint_pulse.setLoopCount(-1)

        self._hint_pulse.start()



    def select_theme(self, key):

        ThemeManager.set_theme(key)

        self.settings_manager.set_theme(key)

        self.sync_theme_buttons()

        self.update()



    def _translucent_text_color(self, accent):

        # A light, slightly-translucent tint rather than a solid
        # opaque color — closer to how the reference lock screen's
        # clock reads: soft, blended with what's behind it, not a flat
        # colored label sitting on top.

        light = accent.lighter(145)

        light.setAlphaF(0.75)

        return light



    def sync_theme_buttons(self):

        for key, btn in self.themeButtons.items():

            btn.setChecked(
                key == ThemeManager.current_name
            )



    def apply_theme_button_styles(self):

        for btn in self.themeButtons.values():

            btn.setStyleSheet(
                """
                QPushButton{

                    background:rgba(255,255,255,0.12);

                    border:1px solid rgba(255,255,255,0.35);

                    border-radius:20px;

                    font-size:16px;

                }

                QPushButton:checked{

                    background:rgba(255,255,255,0.32);

                    border:1px solid rgba(255,255,255,0.75);

                }

                QPushButton:hover{

                    background:rgba(255,255,255,0.22);

                }
                """
            )



    def update_clock(self):

        now = datetime.now()

        self._time_text = now.strftime("%H:%M")

        # "Sun Aug 24" — abbreviated weekday + month, no leading zero
        # on the day, matching the reference exactly rather than the
        # full "Wednesday, September 09" used elsewhere in the app.
        self._date_text = now.strftime("%a %b") + " " + str(now.day)

        self.update()



    def paintEvent(self, event):

        theme = ThemeManager.get()

        accent = QColor(theme.Colors.PRIMARY)


        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)


        # A rich gradient scrim rather than a flat dim — it dims the
        # real animated background enough to keep everything legible,
        # and gives the clock's blended fill something with actual
        # tonal variation to read against, similar to how the
        # reference sits on a gradient wallpaper rather than a flat
        # color.

        gradient = QLinearGradient(0, 0, 0, self.height())

        top_color = accent.darker(280)

        top_color.setAlpha(150)

        bottom_color = accent.darker(170)

        bottom_color.setAlpha(150)

        gradient.setColorAt(0.0, top_color)

        gradient.setColorAt(1.0, bottom_color)

        painter.fillRect(self.rect(), gradient)


        self._paint_clock_block(painter, accent)



    def _paint_clock_block(self, painter, accent):

        area = self.clockArea.geometry()


        date_font = QFont("Segoe UI")

        date_font.setPixelSize(24)

        date_font.setWeight(QFont.Weight(500))


        clock_font = QFont("Segoe UI Semibold")

        clock_font.setPixelSize(96)

        clock_font.setWeight(QFont.Weight(700))


        fm_date = QFontMetrics(date_font)

        fm_clock = QFontMetrics(clock_font)


        date_width = fm_date.horizontalAdvance(self._date_text)

        clock_width = fm_clock.horizontalAdvance(self._time_text)


        center_x = area.center().x()

        date_baseline = area.top() + fm_date.ascent() + 6

        clock_baseline = (
            date_baseline
            + fm_date.descent()
            + 18
            + fm_clock.ascent()
        )


        date_x = center_x - date_width / 2

        clock_x = center_x - clock_width / 2


        # -- date: a simple soft translucent fill. The reference keeps
        # the cutout/rim treatment for the big clock only.

        date_path = QPainterPath()

        date_path.addText(date_x, date_baseline, date_font, self._date_text)


        date_fill = accent.lighter(170)

        date_fill.setAlphaF(0.85)

        painter.setPen(Qt.NoPen)

        painter.setBrush(date_fill)

        painter.drawPath(date_path)


        # -- clock: the actual "cutout" effect —
        # 1. a crisp light rim traced around the glyph outlines
        # 2. a translucent fill laid on top using CompositionMode_
        #    Overlay, so it blends with the gradient already painted
        #    beneath it instead of sitting as flat opaque color — the
        #    digits end up reading as a lightly-tinted window into the
        #    background rather than solid text, with the thin rim
        #    left showing at the edges since the fill doesn't fully
        #    cover it.

        clock_path = QPainterPath()

        clock_path.addText(clock_x, clock_baseline, clock_font, self._time_text)


        rim_pen = QPen(QColor(255, 255, 255, 200))

        rim_pen.setWidthF(2.0)

        rim_pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(rim_pen)

        painter.setBrush(Qt.NoBrush)

        painter.drawPath(clock_path)


        painter.setCompositionMode(
            QPainter.CompositionMode_Screen
        )

        painter.setPen(Qt.NoPen)

        painter.setBrush(QColor(175, 160, 255, 191))

        painter.drawPath(clock_path)


        painter.setCompositionMode(
            QPainter.CompositionMode_SourceOver
        )



    def showEvent(self, event):

        super().showEvent(event)

        self.setFocus()



    # -------------------------
    # DRAG / CLICK / KEY TO DISMISS
    # -------------------------

    def mousePressEvent(self, event):

        self._dragging = True

        self._drag_start_global_y = event.globalPosition().y()

        self._drag_start_widget_y = self.y()



    def mouseMoveEvent(self, event):

        if not self._dragging:
            return

        delta = event.globalPosition().y() - self._drag_start_global_y

        delta = min(0, delta)

        self.move(
            self.x(),
            self._drag_start_widget_y + int(delta)
        )



    def mouseReleaseEvent(self, event):

        if not self._dragging:
            return

        self._dragging = False

        moved_up = self._drag_start_widget_y - self.y()


        # A plain click (barely any movement) counts as "unlock" too —
        # desktop users expect click-anywhere as much as a drag gesture.
        if moved_up > self.DRAG_DISMISS_THRESHOLD or abs(moved_up) < 8:

            self.dismiss()


        else:

            self.snap_back()



    def keyPressEvent(self, event):

        self.dismiss()



    def snap_back(self):

        anim = QPropertyAnimation(self, b"pos")

        anim.setDuration(220)

        anim.setStartValue(self.pos())

        anim.setEndValue(QPoint(0, 0))

        anim.setEasingCurve(QEasingCurve.OutCubic)

        anim.start()

        self._snap_anim = anim



    def dismiss(self):

        if self._dismissed:
            return

        self._dismissed = True

        self.timer.stop()

        self._hint_pulse.stop()

        self.settings_manager.close()


        # Slide the whole lock screen off the top of the window. A
        # QGraphicsOpacityEffect fade layered on top of this looked
        # nice too, but a widget with its own custom paintEvent PLUS a
        # graphics effect PLUS a concurrent position animation is one
        # animation too many — it produced intermittent "paint device
        # painted by two painters" warnings under rapid repaints. The
        # slide alone already reads exactly like "swipe up to unlock".

        slide = QPropertyAnimation(self, b"pos")

        slide.setDuration(340)

        slide.setStartValue(self.pos())

        slide.setEndValue(
            QPoint(self.x(), self.y() - self.height() - 40)
        )

        slide.setEasingCurve(QEasingCurve.OutCubic)

        slide.finished.connect(
            self._finish_dismiss
        )

        slide.start()


        self._slide_anim = slide



    def _finish_dismiss(self):

        self.hide()

        self.unlocked.emit()

        self.deleteLater()
