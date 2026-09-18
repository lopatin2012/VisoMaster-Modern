import os
import sys

# `python main.py --profile` enables the per-stage performance profiler.
if "--profile" in sys.argv:
    os.environ["VISOMASTER_PROFILE"] = "1"
    sys.argv.remove("--profile")

import torch  # noqa: F401  # Must be imported before PySide6 on Python 3.10 (PySide6 mutates typing.Self, breaking torch._dynamo / torchvision)

from app.ui import main_ui
from PySide6 import QtWidgets, QtGui

import qdarktheme
from app.ui.core.proxy_style import ProxyStyle
from app.ui.styles.fluent_theme import apply_fluent_theme
from app.helpers.miscellaneous import ensure_ffmpeg_in_path
from app.helpers import i18n

# Use the bundled dependencies/ffmpeg(.exe) when running without Start*.bat.
ensure_ffmpeg_in_path()

# Inference-only performance defaults (fixed shapes, no autograd needed).
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.set_float32_matmul_precision("high")
torch.set_grad_enabled(False)

if __name__=="__main__":

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(ProxyStyle())
    app.setWindowIcon(QtGui.QIcon("app/ui/core/media/modern_icon.png"))
    i18n.install_qt_translations(app, i18n.load_language())
    apply_fluent_theme("Dark")
    with open("app/ui/styles/dark_styles.qss", "r") as f:
        _style = f.read()
        _style = qdarktheme.load_stylesheet(custom_colors={"primary": "#4facc9"})+'\n'+_style
        app.setStyleSheet(_style)
    window = main_ui.MainWindow()
    window.show()
    exit_code = app.exec()

    # Tearing down the CUDA/TensorRT context after Qt's C++ objects are destroyed
    # crashes during Python finalization on Windows (access violation, pre-existing
    # upstream bug). Flush and hard-exit instead of running interpreter teardown.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)