import logging
import os
import threading
from typing import TYPE_CHECKING, Callable
from functools import partial

import cv2
import numpy as np
from pyqttoast import Toast, ToastPreset, ToastPosition
from qfluentwidgets import MessageBox
from PySide6 import QtWidgets,QtCore,QtGui

from app.ui.widgets import widget_components
from app.ui.widgets.settings_layout_data import SETTINGS_LAYOUT_DATA
import app.helpers.miscellaneous as misc_helpers
from app.helpers import perf, i18n

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.ui.main_ui import MainWindow
    
@QtCore.Slot(str, str, QtWidgets.QWidget)
def create_and_show_messagebox(main_window: 'MainWindow', window_title: str, message: str, parent_widget: QtWidgets.QWidget):
    parent = parent_widget.window() if parent_widget is not None else main_window
    messagebox = MessageBox(i18n.tr(window_title), i18n.tr(message), parent)
    messagebox.yesButton.setText(i18n.tr("OK"))
    messagebox.cancelButton.hide()
    messagebox.exec()

def create_and_show_toast_message(main_window: 'MainWindow', title: str, message: str, style_type='information'):
    style_preset_map = {
        'success': ToastPreset.SUCCESS,
        'warning': ToastPreset.WARNING,
        'error': ToastPreset.ERROR,
        'information': ToastPreset.INFORMATION,
        'success_dark': ToastPreset.SUCCESS_DARK,
        'warning_dark': ToastPreset.WARNING_DARK,
        'error_dark': ToastPreset.ERROR_DARK,
        'information_dark': ToastPreset.INFORMATION_DARK,
    }
    toast = Toast(main_window)
    toast.setTitle(title)
    toast.setText(message)
    toast.setDuration(1400)
    toast.setPosition(ToastPosition.TOP_RIGHT)  # Default: ToastPosition.BOTTOM_RIGHT
    toast.applyPreset(style_preset_map[style_type])  # Apply style preset
    toast.show()
    
def create_control(main_window: 'MainWindow', control_name, control_value):
    main_window.control[control_name] = control_value

def update_control(main_window: 'MainWindow', control_name, control_value, exec_function=None, exec_function_args:list=None):
    exec_function_args = exec_function_args or []
    current_position = main_window.videoSeekSlider.value()

    # Update marker control too
    # Do not update values of control with exec_function (like max threads count) as it would slow down the app heavily
    if main_window.markers.get(current_position) and not exec_function:
        main_window.markers[current_position]['control'][control_name] = control_value

    if exec_function:
        # Only execute the function if the value is different from current
        if main_window.control[control_name] != control_value:
            # By default an exec function definition should have atleast one parameter : MainWindow
            exec_function_args = [main_window, control_value] + exec_function_args
            exec_function(*exec_function_args)
    main_window.control[control_name] = control_value
    refresh_frame(main_window)

def create_default_parameter(main_window: 'MainWindow', parameter_name, parameter_value):
    main_window.default_parameters[parameter_name] = parameter_value

def create_parameter_dict_for_face_id(main_window: 'MainWindow', face_id=0):
    if not main_window.parameters.get(face_id):
        parameters =  main_window.parameters.get(main_window.selected_target_face_id) or main_window.current_widget_parameters or main_window.default_parameters
        if type(parameters)==dict:
            parameters = misc_helpers.ParametersDict(parameters, main_window.default_parameters)
        main_window.parameters[face_id] = parameters.copy()
    # print("Created parameter_dict_for_face_id", face_id)

def update_parameter(main_window: 'MainWindow', parameter_name, parameter_value, enable_refresh_frame=True, exec_function: Callable=None, exec_function_args:list=None):
    exec_function_args = exec_function_args or []
    current_position = main_window.videoSeekSlider.value()
    face_id = main_window.selected_target_face_id

    # Update marker parameters too
    if main_window.markers.get(current_position) and face_id:
        main_window.markers[current_position]['parameters'][face_id][parameter_name] = parameter_value

    if main_window.target_faces and face_id:
        # Store old value and update the parameters with new value
        old_parameter_value = main_window.parameters[face_id][parameter_name]
        main_window.parameters[face_id][parameter_name] = parameter_value

        if enable_refresh_frame:
            refresh_frame(main_window)

        if exec_function and face_id:
            # Only execute the function if the value is different from current
            if main_window.parameters[face_id][parameter_name] != old_parameter_value:
                # By default an exec function definition should have atleast one parameter : MainWindow
                exec_function_args = [main_window, parameter_value] + exec_function_args
                exec_function(*exec_function_args)

    if main_window.current_widget_parameters:
        main_window.current_widget_parameters[parameter_name] = parameter_value

def refresh_frame(main_window: 'MainWindow'):
    video_processor = main_window.video_processor
    if not video_processor.processing:
        video_processor.process_current_frame()

# Function to Hide Elements conditionally from values in LayoutData (Currently supports using Selection box and Toggle button to hide other widgets)
def show_hide_related_widgets(main_window: 'MainWindow', parent_widget, parent_widget_name: str, value1=False, value2=False):
    if main_window.parameter_widgets:
        group_layout_data = parent_widget.group_layout_data #Dictionary contaning layout data of all elements in the group of the parent_widget
        if 'Selection' in parent_widget_name:
            # Loop through all widgets data in the parent widget's group layout data
            for widget_name in group_layout_data.keys():
                # Store the widget object (instance) from the parameters_widgets Dictionary
                current_widget = main_window.parameter_widgets.get(widget_name, False)
                # Check if the current_widget depends on the Parent Widget's (selection) value 
                if group_layout_data[widget_name].get('parentSelection', '') == parent_widget_name and current_widget:
                    # Check if the current_widget has the required value of Parent Widget's (selection) current value to hide/show the current_widget
                    if group_layout_data[widget_name].get('requiredSelectionValue') != parent_widget.currentText():
                        current_widget.hide()
                        current_widget.label_widget.hide()
                        current_widget.reset_default_button.hide()
                        if current_widget.line_edit:
                            current_widget.line_edit.hide()
                    else:
                        current_widget.show()
                        current_widget.label_widget.show()
                        current_widget.reset_default_button.show()
                        if current_widget.line_edit:
                            current_widget.line_edit.show()

        elif 'Toggle' in parent_widget_name:
            # Loop through all widgets data in the parent widget's group layout data
            for widget_name in group_layout_data.keys():
                # Store the widget object (instance) from the parameters_widgets Dictionary
                if not widget_name in main_window.parameter_widgets:
                    continue
                current_widget = main_window.parameter_widgets[widget_name]
                # Check if the current_widget depends on the Parent Widget's (toggle) value 
                parentToggles = group_layout_data[widget_name].get('parentToggle', '')
                if parent_widget_name in parentToggles:
                    if ',' in parentToggles:
                        result = [item.strip() for item in parentToggles.split(',')]
                        parentToggle_ischecked = False
                        for _, required_widget_name in enumerate(result):
                            parentToggle_ischecked = main_window.parameter_widgets[required_widget_name].isChecked()
                        # Check if the current_widget has the required toggle value of Parent Widget's (toggle) checked state to hide/show the current_widget
                        if group_layout_data[widget_name].get('requiredToggleValue') != parentToggle_ischecked:
                            current_widget.hide()
                            current_widget.label_widget.hide()
                            current_widget.reset_default_button.hide()
                            if current_widget.line_edit:
                                current_widget.line_edit.hide()
                        else:
                            current_widget.show()
                            current_widget.label_widget.show()
                            current_widget.reset_default_button.show()
                            if current_widget.line_edit:
                                current_widget.line_edit.show()
                    elif '|' in parentToggles:
                        result = [item.strip() for item in parentToggles.split('|')]
                        parentToggle_ischecked = True
                        # Check if any of the parentToggles are checked
                        for _, required_widget_name in enumerate(result):
                            ischecked = main_window.parameter_widgets[required_widget_name].isChecked()
                            if ischecked:
                                parentToggle_ischecked = True
                                break
                            else:
                                parentToggle_ischecked = False

                        # Check if the current_widget has the required toggle value of Parent Widget's (toggle) checked state to hide/show the current_widget
                        if group_layout_data[widget_name].get('requiredToggleValue') != parentToggle_ischecked:
                            current_widget.hide()
                            current_widget.label_widget.hide()
                            current_widget.reset_default_button.hide()
                            if current_widget.line_edit:
                                current_widget.line_edit.hide()
                        else:
                            current_widget.show()
                            current_widget.label_widget.show()
                            current_widget.reset_default_button.show()
                            if current_widget.line_edit:
                                current_widget.line_edit.show()

                    elif '&' in parentToggles:
                        result = [item.strip() for item in parentToggles.split('&')]
                        parentToggle_ischecked = True
                        # Check if any of the parentToggles are checked
                        for _, required_widget_name in enumerate(result):
                            ischecked = main_window.parameter_widgets[required_widget_name].isChecked()
                            parentToggle_ischecked = parentToggle_ischecked and ischecked

                        # Check if the current_widget has the required toggle value of Parent Widget's (toggle) checked state to hide/show the current_widget
                        if group_layout_data[widget_name].get('requiredToggleValue') != parentToggle_ischecked:
                            current_widget.hide()
                            current_widget.label_widget.hide()
                            current_widget.reset_default_button.hide()
                            if current_widget.line_edit:
                                current_widget.line_edit.hide()
                        else:
                            current_widget.show()
                            current_widget.label_widget.show()
                            current_widget.reset_default_button.show()
                            if current_widget.line_edit:
                                current_widget.line_edit.show()

                    else:
                        parentToggle_ischecked = main_window.parameter_widgets[parentToggles].isChecked()
                        if group_layout_data[widget_name].get('requiredToggleValue') != parentToggle_ischecked:
                            current_widget.hide()
                            current_widget.label_widget.hide()
                            current_widget.reset_default_button.hide()
                            if current_widget.line_edit:
                                current_widget.line_edit.hide()
                        else:
                            current_widget.show()
                            current_widget.label_widget.show()
                            current_widget.reset_default_button.show()
                            if current_widget.line_edit:
                                current_widget.line_edit.show()

            parent_widget.start_animation()

# @misc_helpers.benchmark    
def get_pixmap_from_frame(main_window: 'MainWindow', frame: np.ndarray):
    with perf.timer("preview_pixmap"):
        height, width, channel = frame.shape
        logger.debug("get_pixmap_from_frame: shape=%s dtype=%s contiguous=%s",
                     frame.shape, frame.dtype, frame.flags["C_CONTIGUOUS"])
        if channel == 2:
            # Frame in grayscale
            bytes_per_line = width
            q_img = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_Grayscale8)
        else:
            # Frame is BGR here; Format_BGR888 avoids an extra rgbSwapped() full-frame copy.
            bytes_per_line = 3 * width
            q_img = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_BGR888)
        pixmap = QtGui.QPixmap.fromImage(q_img)
    return pixmap


def update_gpu_memory_progressbar(main_window: 'MainWindow'):
    threading.Thread(target=partial(_update_gpu_memory_progressbar, main_window)).start()

def _update_gpu_memory_progressbar(main_window: 'MainWindow'):
    memory_used, memory_total = main_window.models_processor.get_gpu_memory()
    main_window.gpu_memory_update_signal.emit(memory_used, memory_total)

@QtCore.Slot(int, int)
def set_gpu_memory_progressbar_value(main_window: 'MainWindow', memory_used, memory_total):
    main_window.vramProgressBar.setMaximum(memory_total)
    main_window.vramProgressBar.setValue(memory_used)
    main_window.vramProgressBar.setFormat(f'{round(memory_used/1024,2)} GB / {round(memory_total/1024,2)} GB (%p%)')
    if (memory_used/memory_total)> 0.85:
        main_window.vramProgressBar.setStyleSheet('''
            QProgressBar::chunk {
                background-color: #911414;  /* Set chunk color to green */
            }
        ''')
    else:
        main_window.vramProgressBar.setStyleSheet('''
            QProgressBar::chunk {
                background-color: #16759e;  /* Set chunk color to green */
            }
        ''')
    main_window.vramProgressBar.update()

def clear_gpu_memory(main_window: 'MainWindow'):
    main_window.video_processor.stop_processing()
    main_window.models_processor.clear_gpu_memory()
    main_window.swapfacesButton.setChecked(False)
    main_window.editFacesButton.setChecked(False)
    update_gpu_memory_progressbar(main_window)

    main_window.videoSeekSlider.markers = set()
    main_window.videoSeekSlider.update()

def thumbnail_frame_to_pixmap(frame):
    """Build the 70x70 thumbnail QPixmap from a BGR frame.

    QPixmap is GUI-thread only, so call this from the GUI thread (e.g. a slot),
    never from a worker thread.
    """
    height, width, _ = frame.shape
    bytes_per_line = 3 * width
    q_img = QtGui.QImage(frame.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGB888).rgbSwapped()
    pixmap = QtGui.QPixmap.fromImage(q_img)
    return pixmap.scaled(70, 70, QtCore.Qt.AspectRatioMode.KeepAspectRatio)


def extract_thumbnail_frame(media_file_path, file_type, webcam_index=False, webcam_backend=False):
    """Return the BGR frame to use as a media thumbnail (or None).

    This runs on a worker thread, so it must not create a QPixmap (GUI-thread
    only); callers convert the returned frame with ``thumbnail_frame_to_pixmap``.
    """
    frame = False

    # For non-webcam media, reuse a cached thumbnail if present
    if file_type in ['image', 'video']:
        misc_helpers.ensure_thumbnail_dir()
        file_hash = misc_helpers.get_hash_from_filename(media_file_path)
        thumbnail_path = misc_helpers.get_thumbnail_path(file_hash)
        if misc_helpers.is_file_exists(thumbnail_path):
            cached = misc_helpers.read_image_file(thumbnail_path)
            if cached is not None:
                return cached
    
    # If no cached thumbnail or it's a webcam, proceed with normal frame extraction
    if file_type == 'image':
        frame = misc_helpers.read_image_file(media_file_path)
    elif file_type == 'video':    
        cap = cv2.VideoCapture(media_file_path)
        if not cap.isOpened():
            logger.warning("Could not open video for thumbnail: %s", media_file_path)
            return None
        
        # Get total frames and find the middle frame no
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        middle_frame_no = total_frames//2
        # Seek to the middle frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_no)
        ret, frame = misc_helpers.read_frame(cap)
        cap.release()
            
    elif file_type == 'webcam':
        camera = cv2.VideoCapture(webcam_index, webcam_backend)
        if not camera.isOpened():
            logger.warning("Could not open webcam for thumbnail: %s", webcam_index)
            camera.release()
            return
        ret, frame = misc_helpers.read_frame(camera)
        camera.release()
        if not ret:
            logger.warning("Could not read a frame from webcam: %s", webcam_index)
            return

    if isinstance(frame, np.ndarray):
        # Save thumbnail for future use (image/video only; webcam has no cache path)
        if file_type != 'webcam':
            misc_helpers.save_thumbnail(frame, thumbnail_path)
        return frame
    return None

def set_widgets_values_using_face_id_parameters(main_window: 'MainWindow', face_id=False):
    if (face_id is False) or (not main_window.parameters.get(face_id)):
        # print("Set widgets values using default parameters")
        if main_window.current_widget_parameters:
            parameters = main_window.current_widget_parameters.copy()
        else:
            parameters = main_window.default_parameters
    else:
        # print(f"Set widgets values using face_id {face_id}")
        parameters = main_window.parameters[face_id].copy()
    parameter_widgets = main_window.parameter_widgets
    for parameter_name, parameter_value in parameters.items():
        # temporarily disable refreshing the frame to prevent slowing due to unnecessary processing
        if parameter_widgets.get(parameter_name):
            parameter_widgets[parameter_name].enable_refresh_frame = False
            parameter_widgets[parameter_name].set_value(parameter_value)
            parameter_widgets[parameter_name].enable_refresh_frame = True

def set_control_widgets_values(main_window: 'MainWindow', enable_exec_func = True):
    """
    Set the values of control widgets based on the `control` data in the `main_window`.

    Temporarily disables frame refreshing while setting values to avoid unnecessary processing.
    """
    # Get control values and parameter widgets from the main window
    control = main_window.control.copy()
    parameter_widgets = main_window.parameter_widgets

    # Prepare a dictionary of settings options from layout data
    settings_options = {
        setting_name: setting_data
        for setting_group in SETTINGS_LAYOUT_DATA.values()
        for setting_name, setting_data in setting_group.items()
    }

    # Iterate through control items and update widgets
    for control_name, control_value in control.items():
        widget = parameter_widgets.get(control_name)

        if widget:

            # Temporarily disable frame refresh
            widget.enable_refresh_frame = False

            # Set the widget value
            widget.set_value(control_value)


            if enable_exec_func:
                # Execute any associated function, if defined
                exec_function_data = settings_options[control_name].get('exec_function')
                if exec_function_data:
                    exec_function = partial(
                        exec_function_data, main_window
                    )
                    exec_args = settings_options[control_name].get('exec_fuction_args', [])
                    exec_function(control_value, *exec_args)

            # Re-enable frame refresh
            widget.enable_refresh_frame = True
        
@QtCore.Slot(QtWidgets.QListWidget, bool)
def update_placeholder_visibility(main_window: 'MainWindow', list_widget:QtWidgets.QListWidget, default_hide):
    # """Update the visibility of the placeholder text."""
    # """
    #     The default_hide parameter is used to Hide the placeholder text by default. 
    #     If the default_hide is False, then the visibility of the placeholder text is set using the size of the list_widget 
    # """
    if default_hide:
        is_visible = False
    else:
        is_visible = list_widget.count()==0
    list_widget.placeholder_label.setVisible(is_visible)
    # Set Cursor on the List Widget
    if is_visible:
        list_widget.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    else:
        list_widget.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
    # print("SetVisible", is_visible)
    # print("targetVideosList.count()", list_widget.count())


@QtCore.Slot()
def show_model_loading_dialog(main_window: 'MainWindow'):
    # Reuse a single dialog: recreating it while a previous instance is still
    # alive lets Python GC delete a visible QWidget during event processing,
    # which can crash the native side.
    dialog = getattr(main_window, "model_loading_dialog", None)
    if dialog is None:
        dialog = widget_components.LoadingDialog()
        main_window.model_loading_dialog = dialog
    dialog.show()
    # Never run a nested event loop while a frame is being processed synchronously
    # on the GUI thread (re-entrancy corrupts Qt state and crashes later).
    if not getattr(main_window.video_processor, "processing_single_frame", False):
        QtWidgets.QApplication.processEvents()

@QtCore.Slot()
def hide_model_loading_dialog(main_window: 'MainWindow'):
    dialog = getattr(main_window, "model_loading_dialog", None)
    if dialog is not None:
        dialog.hide()
    if not getattr(main_window.video_processor, "processing_single_frame", False):
        QtWidgets.QApplication.processEvents()
