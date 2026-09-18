"""Headless smoke test for VisoMaster-Modern.

Constructs the main window (offscreen) and checks the widgets/behaviours that have
regressed before (Fluent widget promotions, lists, sliders, VRAM bar, menus, i18n).

Run from the repo root:
    .venv\\Scripts\\python.exe tools\\smoke_test.py

Exit code 0 = pass, 1 = failure(s), 2 = could not even start.
Requires a CUDA device (ModelsProcessor allocates on 'cuda').
"""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import faulthandler  # noqa: E402
import gc  # noqa: E402

faulthandler.enable()
gc.disable()  # avoid GC-triggered C++ teardown while CUDA/Qt are alive

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.helpers.process_exit import hard_exit  # noqa: E402

import torch  # noqa: E402  # must precede PySide6

import contextlib as _contextlib  # noqa: E402
import io as _io  # noqa: E402
with _contextlib.redirect_stdout(_io.StringIO()):
    import qfluentwidgets  # noqa: F401,E402  # silence the "Pro" banner

from PySide6 import QtWidgets  # noqa: E402

FAILURES = []


def check(condition, message):
    print(("  [ok]   " if condition else "  [FAIL] ") + message)
    if not condition:
        FAILURES.append(message)


def main():
    print("== VisoMaster-Modern smoke test ==")

    try:
        from app.helpers import i18n
        from app.ui import main_ui
        from app.version import APP_VERSION
    except Exception as exc:  # noqa: BLE001
        print(f"  [FAIL] import failed: {exc!r}")
        sys.stdout.flush()
        hard_exit(2)

    if not torch.cuda.is_available():
        print("  [!] CUDA is not available; ModelsProcessor may fail to construct.")

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    i18n.install_qt_translations(app, i18n.load_language())

    try:
        window = main_ui.MainWindow()
    except Exception as exc:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print(f"  [FAIL] MainWindow() raised: {exc!r}")
        sys.stdout.flush()
        hard_exit(2)

    check(bool(window.windowTitle()), "window title is set")
    check(APP_VERSION in window.windowTitle(), f"window title contains version {APP_VERSION}")
    check(window.tabWidget.count() == 4, "Control Options has 4 tabs")
    check(len(window.parameter_widgets) > 20, "parameter widgets were created")

    # Standard Qt widgets that must NOT be the Fluent variants (they broke rendering).
    check(type(window.videoSeekSlider) is QtWidgets.QSlider, "videoSeekSlider is a plain QSlider")
    check(type(window.vramProgressBar) is QtWidgets.QProgressBar, "vramProgressBar is a plain QProgressBar")
    for name in ("targetVideosList", "inputFacesList", "targetFacesList", "inputEmbeddingsList"):
        widget = getattr(window, name)
        check(type(widget) is QtWidgets.QListWidget, f"{name} is a plain QListWidget")

    # Top menu must contain the Settings menu with Theme/Language/About.
    top_menus = [m for m in window.topMenuBar.findChildren(QtWidgets.QMenu) if m.parent() is window.topMenuBar]
    titles = {m.title() for m in top_menus}
    settings_menu = next(
        (m for m in top_menus if m.title() in ("Settings", "Настройки", "设置")), None
    )
    check(settings_menu is not None, f"Settings menu present (menus: {sorted(titles)})")
    if settings_menu:
        submenu_titles = {a.menu().title() for a in settings_menu.actions() if a.menu()}
        check("Theme" in submenu_titles or "Тема" in submenu_titles or "主题" in submenu_titles,
              f"Theme submenu present (submenus: {sorted(submenu_titles)})")
        about = next(
            (a for a in settings_menu.actions()
             if a.property("_i18n_src") == "About" or a.text() in ("About", "О программе", "关于")),
            None,
        )
        check(about is not None, "About action present")

    # i18n: switching languages and re-applying must not raise and must translate.
    original_lang = i18n.get_language()
    try:
        for code in ("en", "ru", "zh"):
            try:
                i18n.set_language(code, save=False)
                i18n.apply_to_widgets(window)
                if code == "en":
                    check(i18n.tr("Swap Faces") == "Swap Faces", "en keeps source strings")
                else:
                    check(i18n.tr("Swap Faces") != "Swap Faces", f"{code} translation applied")
            except Exception as exc:  # noqa: BLE001
                check(False, f"language switch to {code} raised: {exc!r}")
    finally:
        i18n.set_language(original_lang, save=False)
        i18n.apply_to_widgets(window)

    print(f"\n{'PASS' if not FAILURES else 'FAIL'}: {len(FAILURES)} failure(s)")
    # Hard exit right here: CUDA/torch teardown after Qt segfaults during finalization
    # (see main.py). Doing it before returning keeps the exit code deterministic.
    sys.stdout.flush()
    sys.stderr.flush()
    hard_exit(0 if not FAILURES else 1)


def _run_in_parent() -> int:
    """Run the checks in a child process and derive a deterministic exit code.

    The child loads CUDA/Qt, whose DLL detach can crash during process teardown on
    Windows (after the result was already printed). The parent stays lightweight and
    reports based on the child's stdout.
    """
    import subprocess

    child = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--child"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    sys.stdout.write(child.stdout)
    ok = "PASS:" in child.stdout and "FAIL:" not in child.stdout
    if not ok:
        sys.stderr.write(child.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    if "--child" in sys.argv:
        main()  # runs the checks and hard-exits inside
    else:
        sys.exit(_run_in_parent())
