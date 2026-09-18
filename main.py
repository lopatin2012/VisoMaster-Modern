import torch  # noqa: F401  # Must be imported before PySide6 on Python 3.10 (PySide6 mutates typing.Self, breaking torch._dynamo / torchvision)

from app.ui import main_ui
from PySide6 import QtWidgets 
import sys

import qdarktheme
from app.ui.core.proxy_style import ProxyStyle
from app.ui.styles.fluent_theme import apply_fluent_theme

if __name__=="__main__":

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(ProxyStyle())
    apply_fluent_theme("Dark")
    with open("app/ui/styles/dark_styles.qss", "r") as f:
        _style = f.read()
        _style = qdarktheme.load_stylesheet(custom_colors={"primary": "#4facc9"})+'\n'+_style
        app.setStyleSheet(_style)
    window = main_ui.MainWindow()
    window.show()
    app.exec()