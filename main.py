import os
import sys
import faulthandler

# Dump a Python stack on native crashes (segfault / access violation) to a file,
# so CUDA/Qt crashes that skip normal tracebacks are still diagnosable.
try:
    _FAULT_LOG = open("faulthandler.log", "a", buffering=1, encoding="utf-8")  # noqa: SIM115
    faulthandler.enable(file=_FAULT_LOG, all_threads=True)
except Exception:  # pylint: disable=broad-exception-caught
    faulthandler.enable(all_threads=True)

# `python main.py --profile` enables the per-stage performance profiler.
if "--profile" in sys.argv:
    os.environ["VISOMASTER_PROFILE"] = "1"
    sys.argv.remove("--profile")

# Configure logging before importing app modules (some call logging.basicConfig early).
from app.helpers.logging_setup import setup_logging  # noqa: E402
from app.helpers.crash_info import install_crash_handler  # noqa: E402

setup_logging()

# Log the faulting DLL/module on native access violations (Windows).
install_crash_handler()

import torch  # noqa: F401  # Must be imported before PySide6 on Python 3.10 (PySide6 mutates typing.Self, breaking torch._dynamo / torchvision)

# qfluentwidgets prints a "Pro" advertisement to stdout on its first import; silence it.
import contextlib as _contextlib
import io as _io
with _contextlib.redirect_stdout(_io.StringIO()):
    import qfluentwidgets as _qfw  # noqa: F401

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

    # Give the process its own AppUserModelID so Windows shows the app's own
    # window icon in the taskbar instead of the python.exe icon.
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VisoMaster-Modern")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(ProxyStyle())
    app.setApplicationName("VisoMaster-Modern")
    _icon_path = "app/ui/core/media/modern_icon.ico"
    if not os.path.isfile(_icon_path):
        _icon_path = "app/ui/core/media/modern_icon.png"
    _app_icon = QtGui.QIcon(_icon_path)
    app.setWindowIcon(_app_icon)
    i18n.install_qt_translations(app, i18n.load_language())
    apply_fluent_theme("Dark")
    with open("app/ui/styles/dark_styles.qss", "r") as f:
        _style = f.read()
        _style = qdarktheme.load_stylesheet(custom_colors={"primary": "#4facc9"})+'\n'+_style
        app.setStyleSheet(_style)
    window = main_ui.MainWindow()
    window.setWindowIcon(_app_icon)
    window.show()
    exit_code = app.exec()

    # Tearing down the CUDA/TensorRT context after Qt's C++ objects are destroyed
    # crashes during Python finalization on Windows (access violation, pre-existing
    # upstream bug). Flush and hard-exit instead of running interpreter teardown.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)