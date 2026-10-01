"""
Small "something happened" notifications - task added, task deleted (with
an Undo action), a focus session logged, and so on.

Usage from anywhere in the app:

    from ui.toast import notify
    notify('Added "Buy milk"', "success")
    notify("Task deleted", "info", action=("Undo", lambda: restore(task)))

ToastHost (created once in app.py, parented to the central widget) is
what actually renders them, stacked bottom-right.
"""

from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from themes.manager import ThemeManager
from utils.color_utils import lighten, rgba
from utils.glass_effects import RefractiveGlassMixin, apply_soft_shadow
from ui.icons import IconGlyph


class _Toaster(QObject):

    # kind is "info" | "success" | "warning" | "error".
    # action is None, or (label: str, callback: Callable[[], None]).
    requested = Signal(str, str, object)


_toaster = _Toaster()


def notify(message, kind="info", action=None):

    _toaster.requested.emit(message, kind, action)


_KIND_ICON = {
    "info": "bell",
    "success": "check",
    "warning": "alert",
    "error": "close",
}


class ToastWidget(RefractiveGlassMixin, QWidget):

    glass_radius = 16

    DURATION_MS = 3200

    DURATION_WITH_ACTION_MS = 6500

    def __init__(self, message, kind, action, on_dismissed, parent=None):

        super().__init__(parent)

        self.setObjectName("toast")

        # Plain QWidget subclasses don't paint their stylesheet
        # background/border by default (QFrame does) - without this the
        # "background: ...; border-radius: ..." below would be invisible.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setFixedWidth(320)

        self._on_dismissed = on_dismissed

        self._dismissing = False

        theme = ThemeManager.get()

        accent = {
            "info": theme.Colors.PRIMARY,
            "success": theme.Colors.GREEN,
            "warning": theme.Colors.ORANGE,
            "error": theme.Colors.RED,
        }.get(kind, theme.Colors.PRIMARY)

        row = QHBoxLayout(self)

        row.setContentsMargins(14, 12, 12, 12)

        row.setSpacing(10)

        self.badge = QWidget()

        self.badge.setFixedSize(26, 26)

        self.badge.setStyleSheet(
            f"background:{rgba(accent, 0.22)}; border-radius:13px;"
        )

        badgeLayout = QHBoxLayout(self.badge)

        badgeLayout.setContentsMargins(0, 0, 0, 0)

        badgeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = IconGlyph(
            _KIND_ICON.get(kind, "bell"),
            size=14,
            color=lighten(accent, 130),
            stroke_width=2.0
        )

        badgeLayout.addWidget(icon)

        self.label = QLabel(message)

        self.label.setWordWrap(True)

        self.label.setStyleSheet(
            f"color:{theme.Colors.TEXT}; font-size:13px; "
            "background:transparent; border:none;"
        )

        row.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignTop)

        row.addWidget(self.label, 1)

        if action is not None:

            label, callback = action

            actionButton = QPushButton(label)

            actionButton.setCursor(Qt.CursorShape.PointingHandCursor)

            actionButton.setStyleSheet(
                f"""
                QPushButton {{
                    color:{lighten(accent, 130)};
                    background:{rgba(accent, 0.16)};
                    border:1px solid {rgba(accent, 0.45)};
                    border-radius:9px;
                    padding:4px 10px;
                    font-size:12px;
                    font-weight:700;
                }}
                QPushButton:hover {{
                    background:{rgba(accent, 0.28)};
                }}
                """
            )

            def fire():

                callback()

                self.dismiss()

            actionButton.clicked.connect(fire)

            row.addWidget(actionButton, 0, Qt.AlignmentFlag.AlignVCenter)

        closeButton = QPushButton()

        closeButton.setFixedSize(20, 20)

        closeButton.setCursor(Qt.CursorShape.PointingHandCursor)

        closeButton.setStyleSheet(
            "QPushButton{background:transparent; border:none;} "
            "QPushButton:hover{background:rgba(255,255,255,0.10); border-radius:10px;}"
        )

        closeIcon = IconGlyph(
            "close",
            size=11,
            color=theme.Colors.TEXT_SECONDARY,
            stroke_width=1.8
        )

        closeLayout = QHBoxLayout(closeButton)

        closeLayout.setContentsMargins(0, 0, 0, 0)

        closeLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        closeLayout.addWidget(closeIcon)

        closeButton.clicked.connect(self.dismiss)

        row.addWidget(closeButton, 0, Qt.AlignmentFlag.AlignTop)

        self.setStyleSheet(
            f"""
            QWidget#toast {{
                background:{theme.Colors.SURFACE_ALT};
                border:1px solid {theme.Colors.BORDER};
                border-radius:16px;
            }}
            """
        )

        apply_soft_shadow(self, blur=30, alpha=110)

        self._effect = QGraphicsOpacityEffect(self)

        self._effect.setOpacity(0.0)

        self.setGraphicsEffect(self._effect)

        self.adjustSize()

        duration = (
            self.DURATION_WITH_ACTION_MS
            if action is not None
            else self.DURATION_MS
        )

        self._timer = QTimer(self)

        self._timer.setSingleShot(True)

        self._timer.timeout.connect(self.dismiss)

        self._timer.start(duration)

    def enterEvent(self, event):

        # Hovering (about to click Undo) shouldn't let the toast vanish
        # under the cursor.

        self._timer.stop()

        super().enterEvent(event)

    def leaveEvent(self, event):

        self._timer.start(1400)

        super().leaveEvent(event)

    def appear(self):

        anim = QPropertyAnimation(self._effect, b"opacity", self)

        anim.setDuration(200)

        anim.setStartValue(0.0)

        anim.setEndValue(1.0)

        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def dismiss(self):

        if self._dismissing:

            return

        self._dismissing = True

        self._timer.stop()

        anim = QPropertyAnimation(self._effect, b"opacity", self)

        anim.setDuration(160)

        anim.setStartValue(self._effect.opacity())

        anim.setEndValue(0.0)

        def finished():

            self._on_dismissed(self)

            self.deleteLater()

        anim.finished.connect(finished)

        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class ToastHost(QWidget):

    # Holds the stack of toasts in the window's bottom-right corner.
    #
    # IMPORTANT: this widget is only ever as big as the toasts it holds
    # (and hidden when there are none). It used to be a transparent
    # full-window overlay, which sat above the whole UI and swallowed
    # every mouse click - Qt delivers a click to the topmost widget under
    # the cursor, and "transparent" only affects painting, not that.

    MARGIN = 22

    GAP = 10

    def __init__(self, parent):

        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._toasts = []

        self.hide()

        _toaster.requested.connect(self._spawn)

    def _spawn(self, message, kind, action):

        toast = ToastWidget(message, kind, action, self._remove, parent=self)

        self._toasts.append(toast)

        self._relayout()

        toast.show()

        toast.appear()

    def _remove(self, toast):

        if toast in self._toasts:

            self._toasts.remove(toast)

        self._relayout()

    def _relayout(self):

        parent = self.parentWidget()

        if parent is None:

            return

        if not self._toasts:

            # Nothing to show, so nothing may sit over the UI.

            self.hide()

            return

        for toast in self._toasts:

            toast.adjustSize()

        width = max(toast.width() for toast in self._toasts)

        height = (
            sum(toast.height() for toast in self._toasts)
            + self.GAP * (len(self._toasts) - 1)
        )

        self.setGeometry(
            parent.width() - self.MARGIN - width,
            parent.height() - self.MARGIN - height,
            width,
            height
        )

        # Oldest at the top, newest at the bottom.

        y = 0

        for toast in self._toasts:

            toast.move(0, y)

            y += toast.height() + self.GAP

        self.show()

        self.raise_()

    def reposition(self):

        self._relayout()
