from typing import TYPE_CHECKING
import json
import logging
import os
import torch
import qdarkstyle
from PySide6 import QtWidgets 
import qdarktheme

if TYPE_CHECKING:
    from app.ui.main_ui import MainWindow
from app.ui.widgets.actions import common_actions as common_widget_actions
from app.ui.styles.fluent_theme import apply_fluent_theme
from app.helpers import i18n, asset_check
from app.version import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)

# Named face-parameter presets. CWD-relative like last_workspace.json; the broad
# `*.json` .gitignore rule keeps it untracked.
PRESETS_FILE = "parameter_presets.json"

#'''
#    Define functions here that has to be executed when value of a control widget (In the settings tab) is changed.
#    The first two parameters should be the MainWindow object and the new value of the control 
#'''

def change_language(main_window: 'MainWindow', selected_language):
    code = i18n.set_language(i18n.code_for_display_name(selected_language))
    i18n.install_qt_translations(QtWidgets.QApplication.instance(), code)
    i18n.apply_to_widgets(main_window)
    main_window.update()


def change_execution_provider(main_window: 'MainWindow', new_provider):
    main_window.video_processor.stop_processing()
    main_window.models_processor.switch_providers_priority(new_provider)
    main_window.models_processor.clear_gpu_memory()
    common_widget_actions.update_gpu_memory_progressbar(main_window)

def change_threads_number(main_window: 'MainWindow', new_threads_number):
    main_window.video_processor.set_number_of_threads(new_threads_number)
    torch.cuda.empty_cache()
    common_widget_actions.update_gpu_memory_progressbar(main_window)


def change_theme(main_window: 'MainWindow', new_theme):

    def get_style_data(filename, theme='dark', custom_colors=None):
        custom_colors = custom_colors or {"primary": "#4facc9"}
        with open(f"app/ui/styles/{filename}", "r") as f: # pylint: disable=unspecified-encoding
            _style = f.read()
            _style = qdarktheme.load_stylesheet(theme=theme, custom_colors=custom_colors)+'\n'+_style
        return _style
    app = QtWidgets.QApplication.instance()

    _style = ''
    if new_theme == "Dark":
        _style = get_style_data('dark_styles.qss', 'dark',)

    elif new_theme == "Light":
        _style = get_style_data('light_styles.qss', 'light',)

    elif new_theme == "Dark-Blue":
        _style = get_style_data('dark_styles.qss', 'dark',) + qdarkstyle.load_stylesheet() # Applica lo stile dark-blue 

    app.setStyleSheet(_style)

    apply_fluent_theme(new_theme)

    main_window.update()  # Aggiorna la finestra principale


def set_theme_from_menu(main_window: 'MainWindow', new_theme):
    main_window.control['ThemeSelection'] = new_theme
    change_theme(main_window, new_theme)


def check_models(main_window: 'MainWindow'):
    from qfluentwidgets import MessageBox

    missing = asset_check.find_missing_models()
    if missing:
        title = i18n.tr("Models Missing")
        shown = "\n".join(missing[:12])
        if len(missing) > 12:
            shown += f"\n… (+{len(missing) - 12})"
        body = f"{i18n.tr('Some model files are missing. Run download_models.py to download them:')}\n\n{shown}"
    else:
        title = i18n.tr("Check Models")
        body = i18n.tr("All model files are present.")

    box = MessageBox(title, body, main_window)
    box.yesButton.setText(i18n.tr("OK"))
    box.cancelButton.hide()
    box.exec()


def show_about(main_window: 'MainWindow'):
    from qfluentwidgets import MessageBox
    content = "\n".join([
        f"{APP_NAME} {APP_VERSION}",
        "",
        i18n.tr("AI face swapping and editing for images, videos and webcam."),
        "",
        i18n.tr("License: GPL-3.0 (see LICENSE). Original VisoMaster by its authors."),
        "",
        "https://github.com/lopatin2012/VisoMaster-Modern",
    ])
    box = MessageBox(i18n.tr("About"), content, main_window)
    box.yesButton.setText(i18n.tr("OK"))
    box.cancelButton.hide()
    box.exec()

def set_video_playback_fps(main_window: 'MainWindow', set_video_fps=False):
    # print("Called set_video_playback_fps()")
    if set_video_fps and main_window.video_processor.media_capture:
        main_window.parameter_widgets['VideoPlaybackCustomFpsSlider'].set_value(main_window.video_processor.fps)

def toggle_virtualcam(main_window: 'MainWindow', toggle_value=False):
    video_processor = main_window.video_processor
    if toggle_value:
        video_processor.enable_virtualcam()
    else:
        video_processor.disable_virtualcam()

def enable_virtualcam(main_window: 'MainWindow', backend):
    print('backend', backend)
    main_window.video_processor.enable_virtualcam(backend=backend)


def _load_presets() -> dict:
    if not os.path.isfile(PRESETS_FILE):
        return {}
    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Failed to read %s", PRESETS_FILE)
        return {}


def _save_presets(presets: dict) -> None:
    with open(PRESETS_FILE, "w", encoding="utf-8") as file:
        json.dump(presets, file, indent=4)


def _warn(main_window: 'MainWindow', title, message):
    common_widget_actions.create_and_show_messagebox(
        main_window, i18n.tr(title), i18n.tr(message), parent_widget=main_window
    )


def save_face_preset(main_window: 'MainWindow'):
    """Save the selected target face's parameters as a named preset."""
    face_id = main_window.selected_target_face_id
    if not face_id:
        _warn(main_window, "No target face selected",
              "Select a target face before saving a preset.")
        return
    name, ok = QtWidgets.QInputDialog.getText(
        main_window, i18n.tr("Save Preset"), i18n.tr("Preset name:")
    )
    name = (name or "").strip()
    if not ok or not name:
        return
    presets = _load_presets()
    presets[name] = dict(main_window.parameters[face_id])
    try:
        _save_presets(presets)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Failed to write %s", PRESETS_FILE)
        _warn(main_window, "Preset Error", "Could not save the preset.")


def apply_face_preset(main_window: 'MainWindow'):
    """Apply a saved preset to the selected target face."""
    face_id = main_window.selected_target_face_id
    if not face_id:
        _warn(main_window, "No target face selected",
              "Select a target face before applying a preset.")
        return
    presets = _load_presets()
    if not presets:
        _warn(main_window, "No Presets", "No presets saved yet.")
        return
    name, ok = QtWidgets.QInputDialog.getItem(
        main_window, i18n.tr("Apply Preset"), i18n.tr("Preset:"), sorted(presets), 0, False
    )
    if not ok or not name:
        return
    # Only overwrite keys the preset knows about, keeping any newer parameters.
    target = main_window.parameters[face_id]
    for key, value in presets.get(name, {}).items():
        if key in main_window.default_parameters:
            target[key] = value
    common_widget_actions.set_widgets_values_using_face_id_parameters(main_window, face_id=face_id)
    common_widget_actions.refresh_frame(main_window)


def delete_face_preset(main_window: 'MainWindow'):
    """Delete a saved preset."""
    presets = _load_presets()
    if not presets:
        _warn(main_window, "No Presets", "No presets saved yet.")
        return
    name, ok = QtWidgets.QInputDialog.getItem(
        main_window, i18n.tr("Delete Preset"), i18n.tr("Preset:"), sorted(presets), 0, False
    )
    if not ok or not name or name not in presets:
        return
    presets.pop(name, None)
    try:
        _save_presets(presets)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Failed to write %s", PRESETS_FILE)
        _warn(main_window, "Preset Error", "Could not delete the preset.")