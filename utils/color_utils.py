"""Small colour helpers shared by the themed widgets."""

from PySide6.QtGui import QColor


def parse_color(value):

    # Theme palettes mix "#RRGGBB" with CSS-style "rgba(r,g,b,a)" (a is
    # 0..1); QColor only understands the first, so handle both here.

    if isinstance(value, QColor):

        return QColor(value)

    text = str(value).strip()

    if text.lower().startswith("rgba("):

        parts = [
            part.strip()
            for part in text[text.index("(") + 1:text.rindex(")")].split(",")
        ]

        c = QColor(int(parts[0]), int(parts[1]), int(parts[2]))

        c.setAlphaF(float(parts[3]))

        return c

    return QColor(text)


def qcolor(color, alpha=None):

    # Accepts "#RRGGBB", "rgba(...)", a colour name, or a QColor.
    # `alpha` is 0..1 and overrides whatever alpha the input had.

    c = parse_color(color)

    if alpha is not None:

        c.setAlphaF(max(0.0, min(1.0, alpha)))

    return c


def rgba(color, alpha):

    # QSS colour string: rgba(r,g,b,a) with a in 0..1.

    c = parse_color(color)

    return f"rgba({c.red()},{c.green()},{c.blue()},{alpha:.3f})"


def lighten(color, factor=115):

    return parse_color(color).lighter(factor).name()


def darken(color, factor=115):

    return parse_color(color).darker(factor).name()


def mix(a, b, t):

    # Linear blend of two colours, t=0 -> a, t=1 -> b. Returns "#RRGGBB".

    ca, cb = parse_color(a), parse_color(b)

    def lerp(x, y):

        return round(x + (y - x) * t)

    return QColor(
        lerp(ca.red(), cb.red()),
        lerp(ca.green(), cb.green()),
        lerp(ca.blue(), cb.blue())
    ).name()
