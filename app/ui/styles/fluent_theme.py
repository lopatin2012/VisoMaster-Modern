"""Fluent UI theming for VisoMaster-Modern.

qfluentwidgets styles its own widgets (SwitchButton, ComboBox, Slider, ...) via
per-widget stylesheets, so this module only needs to flip the global qfw theme and
accent color. The standard Qt widgets that remain (dock widgets, tabs, lists, menus)
are still styled by the qdarktheme/QSS layer applied in ``main.py`` / ``change_theme``.
"""

from qfluentwidgets import Theme, setTheme, setThemeColor

# Matches the accent color used by the existing QSS themes.
ACCENT_COLOR = "#4facc9"


def apply_fluent_theme(theme_name: str = "Dark") -> None:
    """Apply the qfluentwidgets theme/accent. Call after QApplication exists."""
    theme = Theme.LIGHT if theme_name == "Light" else Theme.DARK
    setTheme(theme, save=False)
    setThemeColor(ACCENT_COLOR, save=False)
