"""App-wide Qt stylesheets. Each function takes a palette (theme.Colors) and returns QSS text."""


def dark_qss(C):
    """Every dark theme, and Custom."""

    return f"""
QMainWindow {{
    background: {C.BACKGROUND};
}}

QWidget {{
    background: transparent;
    color: {C.TEXT};
    font-family: "Helvetica";
    font-size: 11pt;
}}

QFrame {{
    background: transparent;
    border: none;
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QScrollBar:vertical {{
    width: 8px;
    background: transparent;
}}

QScrollBar::handle:vertical {{
    background: rgba(255,255,255,0.12);
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(255,255,255,0.22);
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QPushButton {{
    background: transparent;
    border: none;
}}

QLineEdit {{
    background: {C.GLASS};
    border: 1px solid {C.BORDER};
    border-radius: 12px;
    padding: 10px 14px;
    color: {C.TEXT};
}}

QLineEdit:focus {{
    border: 1px solid {C.PRIMARY};
}}

QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QToolTip {{
    background: {C.SURFACE_ALT};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    padding: 6px;
}}
"""


def light_qss(C):
    """The Light theme."""

    return f"""
QMainWindow {{
    background:{C.BACKGROUND};
}}

QWidget {{
    background:transparent;
    color:{C.TEXT};
    font-family:"Segoe UI";
}}

QFrame {{
    border:none;
}}

QPushButton {{
    background:transparent;
    border:none;
}}

QLineEdit {{
    background:{C.SURFACE};
    border:1px solid {C.BORDER};
    border-radius:12px;
    padding:10px 14px;
    color:{C.TEXT};
}}

QScrollBar:vertical {{
    width:8px;
    background:transparent;
}}

QScrollBar::handle:vertical {{
    background:rgba(0,0,0,0.15);
    border-radius:4px;
}}
"""


def sakura_qss(C):
    """The Sakura theme."""

    return f"""
QMainWindow {{
    background:{C.BACKGROUND};
}}

QWidget {{
    background:transparent;
    color:{C.TEXT};
    font-family:"Segoe UI";
}}

QFrame {{
    border:none;
}}

QLineEdit {{
    background:{C.SURFACE_ALT};
    border: 1px solid {C.BORDER};
    border-radius:14px;
    padding:10px;
    color:{C.TEXT};
}}

QScrollBar::handle:vertical {{
    background:{C.PRIMARY};
    border-radius:4px;
}}
"""
