"""Lightweight, dictionary-based localization for VisoMaster-Modern.

No Qt ``.ts``/``.qm`` toolchain: English source strings are used as keys and looked
up in ``TRANSLATIONS`` at runtime. The interface language is applied live and saved
with ``QSettings``.

Widget helpers store the original English source on the widget (dynamic property
``_i18n_src`` / ``_i18n_tip``) so switching back to English works too.
"""

from PySide6 import QtCore, QtGui, QtWidgets

LANGUAGES = [("en", "English"), ("ru", "Русский")]
_DEFAULT = "en"
_current = _DEFAULT

_SETTINGS = QtCore.QSettings("VisoMaster-Modern", "VisoMaster-Modern")
_qt_translator = None


def get_language() -> str:
    return _current


def load_language() -> str:
    global _current
    value = _SETTINGS.value("ui/language", _DEFAULT)
    _current = value if value in dict(LANGUAGES) else _DEFAULT
    return _current


def set_language(code: str, save: bool = True) -> str:
    global _current
    _current = code if code in dict(LANGUAGES) else _DEFAULT
    if save:
        _SETTINGS.setValue("ui/language", _current)
    return _current


def language_display_name() -> str:
    return dict(LANGUAGES).get(_current, "English")


def code_for_display_name(display_name: str) -> str:
    for code, name in LANGUAGES:
        if name == display_name:
            return code
    return _DEFAULT


def tr(text):
    if not text:
        return text
    if _current == "en":
        return text
    return TRANSLATIONS.get(_current, {}).get(text, text)


def install_qt_translations(app, language_code: str) -> None:
    """Install Qt's own translations so standard dialogs (OK/Cancel, file/color
    pickers, ...) use the selected language instead of English.
    """
    global _qt_translator
    if _qt_translator is not None:
        app.removeTranslator(_qt_translator)
        _qt_translator = None
    if not language_code or language_code == "en":
        return
    translations_path = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.TranslationsPath)
    translator = QtCore.QTranslator()
    if translator.load(f"qtbase_{language_code}", translations_path) or \
            translator.load(f"qt_{language_code}", translations_path):
        app.installTranslator(translator)
        _qt_translator = translator


# --- widget helpers -----------------------------------------------------------------

def _apply_text(widget, text: str) -> None:
    if isinstance(widget, QtWidgets.QGroupBox):
        widget.setTitle(text)
    elif isinstance(widget, (QtWidgets.QAbstractButton, QtWidgets.QLabel, QtGui.QAction)):
        widget.setText(text)
    elif isinstance(widget, QtWidgets.QMenu):
        widget.setTitle(text)
    elif hasattr(widget, "setText"):
        widget.setText(text)


def _current_text(widget) -> str:
    if isinstance(widget, QtWidgets.QGroupBox):
        return widget.title()
    if isinstance(widget, (QtWidgets.QAbstractButton, QtWidgets.QLabel, QtGui.QAction)):
        return widget.text()
    if isinstance(widget, QtWidgets.QMenu):
        return widget.title()
    return ""


def set_widget_text(widget, source: str) -> None:
    widget.setProperty("_i18n_src", source)
    _apply_text(widget, tr(source))


def set_widget_tooltip(widget, source: str) -> None:
    widget.setProperty("_i18n_tip", source)
    widget.setToolTip(tr(source))


def _retranslate_one(widget) -> None:
    if isinstance(widget, QtWidgets.QTabWidget):
        for index in range(widget.count()):
            key = f"_i18n_tab_{index}"
            source = widget.property(key) or widget.tabText(index)
            if source:
                widget.setProperty(key, source)
                widget.setTabText(index, tr(source))

    source = widget.property("_i18n_src")
    if source is None:
        current = _current_text(widget)
        if current:
            widget.setProperty("_i18n_src", current)
            source = current
    if source:
        _apply_text(widget, tr(source))

    tip = widget.property("_i18n_tip")
    if tip:
        widget.setToolTip(tr(tip))

    if isinstance(widget, QtWidgets.QLineEdit):
        placeholder = widget.property("_i18n_ph")
        if placeholder is None:
            current_placeholder = widget.placeholderText()
            if current_placeholder:
                widget.setProperty("_i18n_ph", current_placeholder)
                placeholder = current_placeholder
        if placeholder:
            widget.setPlaceholderText(tr(placeholder))

    if isinstance(widget, (QtWidgets.QMainWindow, QtWidgets.QDialog, QtWidgets.QDockWidget)):
        title = widget.property("_i18n_title") or widget.windowTitle()
        if title:
            widget.setProperty("_i18n_title", title)
            widget.setWindowTitle(tr(title))


def apply_to_widgets(root) -> None:
    """(Re)translate ``root`` and all of its children in place."""
    _retranslate_one(root)
    for obj in root.findChildren(QtCore.QObject):
        if isinstance(obj, (QtWidgets.QWidget, QtGui.QAction)):
            _retranslate_one(obj)


# --- translations -------------------------------------------------------------------

TRANSLATIONS = {
    "ru": {
        # Categories
        "Face Restorer": "Восстановление лица",
        "Swapper": "Сваппер",
        "Face Landmarks Correction": "Коррекция ключевых точек",
        "Face Similarity": "Схожесть лиц",
        "Face Mask": "Маска лица",
        "Face Color Correction": "Цветокоррекция лица",
        "Blend Adjustments": "Настройки смешивания",
        "Appearance": "Внешний вид",
        "General": "Общие",
        "Video Settings": "Настройки видео",
        "Auto Swap": "Автосвап",
        "Detectors": "Детекторы",
        "DFM Settings": "Настройки DFM",
        "Frame Enhancer": "Улучшение кадров",
        "Webcam Settings": "Настройки веб-камеры",
        "Virtual Camera": "Виртуальная камера",
        "Face Recognition": "Распознавание лиц",
        "Embedding Merge Method": "Метод объединения эмбеддингов",
        "Media Selection": "Выбор медиа",

        # Common labels
        "Alignment": "Выравнивание",
        "Animation Region": "Область анимации",
        "Blend": "Смешивание",
        "Crop Scale": "Масштаб кропа",
        "Enable Face Expression Restorer": "Восстановление выражения",
        "Enable Face Restorer": "Восстановление лица",
        "Enable Face Restorer 2": "Восстановление лица 2",
        "Expression Friendly Factor": "Коэффициент выразительности",
        "Fidelity Weight": "Вес точности",
        "Normalize Lips": "Нормализация губ",
        "Normalize Lips Threshold": "Порог нормализации губ",
        "Restorer Type": "Тип ресторера",
        "Retargeting Eyes": "Перенацеливание глаз",
        "Retargeting Eyes Multiplier": "Множитель перенацеливания глаз",
        "Retargeting Lips": "Перенацеливание губ",
        "Retargeting Lips Multiplier": "Множитель перенацеливания губ",
        "VY Ratio": "Коэффициент VY",
        "View Face Compare": "Сравнение лиц",
        "View Face Mask": "Маска лица",

        # Swapper labels
        "5 - Keypoints Adjustments": "Настройки 5 ключевых точек",
        "AMP Morph Factor": "Коэффициент морфинга AMP",
        "Amount": "Количество",
        "AutoColor Transfer": "Перенос AutoColor",
        "Background": "Фон",
        "Background Blur": "Размытие фона",
        "Blend Amount": "Степень смешивания",
        "Blue": "Синий",
        "Border Blur": "Размытие границ",
        "Bottom Border": "Нижняя граница",
        "Brightness": "Яркость",
        "Color Adjustments": "Настройки цвета",
        "Compression": "Сжатие",
        "Contrast": "Контраст",
        "DFL XSeg Mask": "Маска DFL XSeg",
        "DFM Model": "Модель DFM",
        "Differencing": "Разностное смешивание",
        "EyeGlasses": "Очки",
        "Eyes Blend Amount": "Степень смешивания глаз",
        "Eyes Feather Blend": "Мягкое смешивание глаз",
        "Eyes Size Factor": "Коэффициент размера глаз",
        "Eyes Spacing Offset": "Смещение межглазного расстояния",
        "Eyes/Mouth Blur": "Размытие глаз/рта",
        "Face": "Лицо",
        "Face Adjustments": "Настройки лица",
        "Face Blur": "Размытие лица",
        "Face Likeness": "Схожесть лица",
        "Face Parser Mask": "Маска Face Parser",
        "Face Scale Amount": "Масштаб лица",
        "Final Blend": "Финальное смешивание",
        "Final Blend Amount": "Степень финального смешивания",
        "Gamma": "Гамма",
        "Green": "Зелёный",
        "Hair": "Волосы",
        "Hair Makeup": "Макияж волос",
        "Hue": "Оттенок",
        "JPEG Compression": "Сжатие JPEG",
        "Keypoints Scale": "Масштаб ключевых точек",
        "Keypoints X-Axis": "Ключевые точки по X",
        "Keypoints Y-Axis": "Ключевые точки по Y",
        "Left Border": "Левая граница",
        "Left Eye": "Левый глаз",
        "Left Eye:   X": "Левый глаз:   X",
        "Left Eye:   Y": "Левый глаз:   Y",
        "Left Eyebrow": "Левая бровь",
        "Left Mouth:   X": "Левый угол рта:   X",
        "Left Mouth:   Y": "Левый угол рта:   Y",
        "Lips Makeup": "Макияж губ",
        "Lower Lip": "Нижняя губа",
        "Mouth": "Рот",
        "Mouth Blend Amount": "Степень смешивания рта",
        "Mouth Feather Blend": "Мягкое смешивание рта",
        "Mouth Size Factor": "Коэффициент размера рта",
        "Neck": "Шея",
        "Noise": "Шум",
        "Nose": "Нос",
        "Nose:   X": "Нос:   X",
        "Nose:   Y": "Нос:   Y",
        "Occluder/DFL XSeg Blur": "Размытие Occluder XSeg",
        "Occlusion Mask": "Маска окклюзии",
        "Overall Mask Blend Amount": "Общее смешивание маски",
        "RCT Color Transfer": "Перенос цвета RCT",
        "Red": "Красный",
        "Restore Eyes": "Восстановить глаза",
        "Restore Mouth": "Восстановить рот",
        "Right Border": "Правая граница",
        "Right Eye": "Правый глаз",
        "Right Eye:   X": "Правый глаз:   X",
        "Right Eye:   Y": "Правый глаз:   Y",
        "Right Eyebrow": "Правая бровь",
        "Right Mouth:   X": "Правый угол рта:   X",
        "Right Mouth:   Y": "Правый угол рта:   Y",
        "Saturation": "Насыщенность",
        "Sharpness": "Резкость",
        "Similarity Threshold": "Порог схожести",
        "Size": "Размер",
        "Strength": "Сила",
        "Swapper Model": "Модель сваппера",
        "Swapper Resolution": "Разрешение сваппера",
        "Text Masking": "Текстовая маска",
        "Text Masking Entry": "Ввод текстовой маски",
        "Top Border": "Верхняя граница",
        "Transfer Type": "Тип переноса",
        "Upper Lip": "Верхняя губа",
        "X Eyes Offset": "Смещение глаз по X",
        "X Eyes Radius Factor": "Коэффициент радиуса глаз по X",
        "X Mouth Offset": "Смещение рта по X",
        "X Mouth Radius Factor": "Коэффициент радиуса рта по X",
        "Y Eyes Offset": "Смещение глаз по Y",
        "Y Eyes Radius Factor": "Коэффициент радиуса глаз по Y",
        "Y Mouth Offset": "Смещение рта по Y",
        "Y Mouth Radius Factor": "Коэффициент радиуса рта по Y",

        # Settings labels
        "Auto Rotation": "Автоповорот",
        "Detect From Points": "Детекция по точкам",
        "Detect Score": "Порог детекции",
        "Enable Frame Enhancer": "Включить улучшение кадров",
        "Enable Landmark Detection": "Детекция ключевых точек",
        "Face Detect Model": "Модель детекции лиц",
        "Frame Enhancer Type": "Тип улучшения кадров",
        "Input Faces Include Subfolders": "Подпапки (исходные лица)",
        "Landmark Detect Model": "Модель детекции точек",
        "Landmark Detect Score": "Порог детекции точек",
        "Manual Rotation": "Ручной поворот",
        "Max No of Faces to Detect": "Макс. лиц для детекции",
        "Maximum DFM Models to use": "Макс. число DFM-моделей",
        "Number of Threads": "Число потоков",
        "Providers Priority": "Приоритет провайдеров",
        "Recognition Model": "Модель распознавания",
        "Rotation Angle": "Угол поворота",
        "Send Frames to Virtual Camera": "Отправлять в вирт. камеру",
        "Set Custom Video Playback FPS": "Свой FPS воспроизведения",
        "Show Bounding Boxes": "Показывать рамки лиц",
        "Show Landmarks": "Показывать ключевые точки",
        "Swapping Similarity Type": "Тип схожести при свапе",
        "Target Media Include Subfolders": "Подпапки (целевые медиа)",
        "Theme": "Тема",
        "Video Playback FPS": "FPS воспроизведения",
        "Virtual Camera Backend": "Бэкенд виртуальной камеры",
        "Webcam Backend": "Бэкенд веб-камеры",
        "Webcam FPS": "FPS веб-камеры",
        "Webcam Max No": "Макс. число веб-камер",
        "Webcam Resolution": "Разрешение веб-камеры",
        "Language": "Язык",

        # Face editor labels
        "Blur Amount": "Степень размытия",
        "Enable Face Pose/Expression Editor": "Редактор позы/выражения",
        "Eye Wink": "Подмигивание",
        "EyeBrows Direction": "Направление бровей",
        "EyeBrows Makeup": "Макияж бровей",
        "EyeGaze Horizontal": "Взгляд по горизонтали",
        "EyeGaze Vertical": "Взгляд по вертикали",
        "Eyes Close <--> Open Ratio": "Глаза: закрыты <--> открыты (коэф.)",
        "Face Editor Type": "Тип редактора лица",
        "Face Makeup": "Макияж лица",
        "Head Pitch": "Наклон головы",
        "Head Roll": "Крен головы",
        "Head Yaw": "Поворот головы",
        "Lips Close <--> Open Ratio": "Губы: закрыты <--> открыты (коэф.)",
        "Lips Close <--> Open Value": "Губы: закрыты <--> открыты (знач.)",
        "Mouth Grin": "Ухмылка",
        "Mouth Pouting": "Надутые губы",
        "Mouth Pursing": "Поджатые губы",
        "Mouth Smile": "Улыбка",
        "X-Axis Movement": "Движение по X",
        "Y-Axis Movement": "Движение по Y",
        "Z-Axis Movement": "Движение по Z",

        # UI strings
        "Add Marker": "Добавить маркер",
        "Browse Folder": "Выбрать папку",
        "Choose Input Faces Folder": "Выбрать папку исходных лиц",
        "Choose Target Media Folder": "Выбрать папку целевых медиа",
        "Clear Faces": "Очистить лица",
        "Clear VRAM": "Очистить VRAM",
        "Common": "Общие",
        "Control Options": "Параметры управления",
        "Edit": "Правка",
        "Edit Faces": "Редактировать лица",
        "Exit": "Выход",
        "Face Editor": "Редактор лица",
        "Face Swap": "Свап лиц",
        "Faces Panel": "Лица",
        "File": "Файл",
        "Find Faces": "Найти лица",
        "Frame Number": "Номер кадра",
        "Include Images": "Включать изображения",
        "Include Videos": "Включать видео",
        "Include Webcams": "Включать веб-камеры",
        "Input Faces": "Исходные лица",
        "Load Embeddings": "Загрузить эмбеддинги",
        "Load Saved Workspace": "Загрузить сохранённую сессию",
        "Load Source Image Files": "Загрузить файлы исходных лиц",
        "Load Source Images Folder": "Загрузить папку исходных лиц",
        "Load Target Image/Video Files": "Загрузить целевые изображения/видео",
        "Load Target Images/Videos Folder": "Загрузить папку целевых медиа",
        "Media Panel": "Медиа",
        "Move to Next Marker": "К следующему маркеру",
        "Move to Previous Marker": "К предыдущему маркеру",
        "Open Embedding File": "Открыть файл эмбеддингов",
        "Output Directory": "Папка вывода",
        "Parameters Panel": "Параметры",
        "Remove Marker": "Удалить маркер",
        "Save Current Workspace": "Сохранить сессию",
        "Save Embedding": "Сохранить эмбеддинг",
        "Save Embedding As": "Сохранить эмбеддинг как",
        "Save Embeddings": "Сохранить эмбеддинги",
        "Save Embeddings As": "Сохранить эмбеддинги как",
        "Save Image": "Сохранить изображение",
        "Search Embeddings": "Поиск эмбеддингов",
        "Search Faces": "Поиск лиц",
        "Search Videos/Images": "Поиск видео/фото",
        "Select Face Images Path": "Выберите путь к изображениям лиц",
        "Select Videos/Images Path": "Выберите путь к видео/изображениям",
        "Settings": "Настройки",
        "Swap Faces": "Свапнуть лица",
        "Target Videos and Input Faces": "Целевые видео и исходные лица",
        "Target Videos/Images": "Целевые видео/изображения",
        "Test": "Тест",
        "VIew Face Compare": "Сравнение лиц",
        "View": "Вид",
        "View Face Mask": "Маска лица",
        "View Fullscreen (F11)": "Полный экран (F11)",
        "VisoMaster v0.1.5": "VisoMaster-Modern",

        # Settings help
        "Select the interface language": "Выберите язык интерфейса",
        "Automatically Swap all faces using selected Source Faces/Embeddings when loading an video/image file": "Автоматически свапать все лица выбранными исходными лицами/эмбеддингами при загрузке видео/изображения",
        "Automatically rotate the input to detect faces in various orientations.": "Автоматически поворачивать вход для детекции лиц в разных ориентациях.",
        "Blends the enhanced results back into the original frame.": "Смешивает улучшенный результат с исходным кадром.",
        "Choose the ArcFace model to be used for comparing the similarity of faces.": "Выберите модель ArcFace для сравнения схожести лиц.",
        "Choose the backend based on the Virtual Camera you have set up": "Выберите бэкенд в зависимости от настроенной виртуальной камеры",
        "Choose the backend for accessing webcam input.": "Выберите бэкенд для доступа к веб-камере.",
        "Choose the type of similarity calculation for face detection and matching during the face swapping process.": "Выберите тип расчёта схожести для детекции и сопоставления лиц при свапе.",
        "Draw bounding boxes to all detected faces in the frame": "Рисовать рамки вокруг всех найденных лиц в кадре",
        "Enable detection of faces from specified landmark points.": "Включить детекцию лиц по заданным ключевым точкам.",
        "Enable frame enhancement for video inputs to improve visual quality.": "Включить улучшение кадров видео для повышения качества.",
        "Enable or disable facial landmark detection, which is used to refine face alignment.": "Включить или отключить детекцию ключевых точек для уточнения выравнивания лица.",
        "Include all files from Subfolders when choosing Input Faces Folder": "Включать все файлы из подпапок при выборе папки исходных лиц",
        "Include all files from Subfolders when choosing Target Media Folder": "Включать все файлы из подпапок при выборе папки целевых медиа",
        "Manually set the FPS to be used when playing the video": "Вручную задать FPS воспроизведения видео",
        "Rotate the face detector to better detect faces at different angles.": "Поворачивать детектор лиц для лучшей детекции под разными углами.",
        "Select the face detection model to use for detecting faces in the input image or video.": "Выберите модель детекции лиц для входного изображения или видео.",
        "Select the landmark detection model, where different models detect varying numbers of facial landmarks.": "Выберите модель детекции ключевых точек: разные модели находят разное число точек.",
        "Select the maximum number of webcam streams to allow for face swapping.": "Выберите максимальное число веб-камер для свапа.",
        "Select the maximum resolution for webcam input.": "Выберите максимальное разрешение входа веб-камеры.",
        "Select the method to merge facial embeddings. \"Mean\" averages the embeddings, while \"Median\" selects the middle value, providing more robustness to outliers.": "Выберите метод объединения эмбеддингов лиц. \"Mean\" усредняет, \"Median\" берёт медиану — устойчивее к выбросам.",
        "Select the providers priority to be used with the system.": "Выберите приоритет провайдеров выполнения.",
        "Select the theme to be used": "Выберите используемую тему",
        "Select the type of frame enhancement to apply, based on the content and resolution requirements.": "Выберите тип улучшения кадров в зависимости от контента и разрешения.",
        "Send the swapped video/webcam output to virtual camera for using in external applications": "Отправлять результат свапа в виртуальную камеру для внешних приложений",
        "Set number of execution threads while playing and recording. Depends strongly on GPU VRAM.": "Число потоков выполнения при проигрывании и записи. Сильно зависит от объёма VRAM.",
        "Set the confidence score threshold for face detection. Higher values ensure more confident detections but may miss some faces.": "Порог уверенности детекции лиц. Большие значения надёжнее, но могут пропустить часть лиц.",
        "Set the confidence score threshold for facial landmark detection.": "Порог уверенности детекции ключевых точек лица.",
        "Set the maximum FPS of the video when playing": "Максимальный FPS видео при проигрывании",
        "Set the maximum frames per second (FPS) for webcam input.": "Максимальный FPS для входа веб-камеры.",
        "Set the maximum number of faces to detect in a frame": "Максимальное число лиц для детекции в кадре",
        "Set this to the angle of the input face angle to help with laying down/upside down/etc. Angles are read clockwise.": "Задайте угол входного лица (лёжа/вверх ногами и т.п.). Углы отсчитываются по часовой стрелке.",
        "Show Landmarks in realtime.": "Показывать ключевые точки в реальном времени.",

        # Common help
        "Adjust the fidelity weight to control how closely the restoration preserves the original face details.": "Настройте вес точности: чем выше, тем ближе восстановление к деталям оригинала.",
        "Adjusting or modifying the position, shape, or movement of the lips during the facial restoration process. It overrides the Animation Region settings, meaning that the Animation Region will be ignored.": "Настройка положения, формы или движения губ при восстановлении лица. Переопределяет область анимации (она игнорируется).",
        "Adjusting or redirecting the gaze or movement of the eyes during the facial restoration process. It overrides the Animation Region settings, meaning that the Animation Region will be ignored.": "Настройка или перенаправление взгляда/движения глаз при восстановлении лица. Переопределяет область анимации (она игнорируется).",
        "Changes swap crop scale. Increase the value to capture the face more distantly.": "Изменяет масштаб кропа при свапе. Увеличьте, чтобы захватить лицо дальше.",
        "Changes the vy ratio for crop scale. Increase the value to capture the face more distantly.": "Изменяет коэффициент VY для масштаба кропа. Увеличьте, чтобы захватить лицо дальше.",
        "Control the blend ratio between the restored face and the swapped face.": "Управляет степенью смешивания восстановленного и свапнутого лица.",
        "Control the expression similarity between the driving face and the swapped face.": "Управляет схожестью выражения между ведущим и свапнутым лицом.",
        "Enable the use of a face restoration model to improve the quality of the face after swapping.": "Включает модель восстановления лица для повышения качества после свапа.",
        "Enabled the use of the LivePortrait face expression model to restore facial expressions after swapping.": "Включает модель выражения лица LivePortrait для восстановления мимики после свапа.",
        "Multiplier value for Retargeting Eyes.": "Множитель для перенацеливания глаз.",
        "Multiplier value for Retargeting Lips.": "Множитель для перенацеливания губ.",
        "Normalize the lips during the facial restoration process.": "Нормализует губы при восстановлении лица.",
        "Select the alignment method for restoring the face to its original or blended position.": "Выберите метод выравнивания для возврата лица в исходное или смешанное положение.",
        "Select the model type for face restoration.": "Выберите тип модели восстановления лица.",
        "Show Face Compare": "Сравнение лиц",
        "Show Face Mask": "Маска лица",
        "The facial region involved in the restoration process.": "Область лица, участвующая в восстановлении.",
        "Threshold value for Normalize Lips.": "Порог нормализации губ.",

        # Swapper help
        "A rectangle with adjustable bottom, left, right, top, and sides that masks the swapped face result back into the original image.": "Прямоугольник с настраиваемыми границами, который маскирует результат свапа обратно в исходное изображение.",
        "AMP Morph Factor for DFM AMP Models": "Коэффициент морфинга AMP для DFM AMP-моделей",
        "Add noise to swapped face.": "Добавляет шум к свапнутому лицу.",
        "Adjust the JPEG Compression amount": "Настройка степени сжатия JPEG",
        "Adjust the blend value.": "Настройка степени смешивания.",
        "Adjust the blending of eyes border. Increase this to show more of the original eyes. Decrease this to show more of the swapped eyes.": "Настройка смешивания границ глаз. Больше — видно больше оригинальных глаз, меньше — свапнутых.",
        "Adjust the blur of mask border.": "Настройка размытия границ маски.",
        "Adjust the border of Mouth blending. Increase this to show more of the original Mouth. Decrease this to show more of the swapped Mouth.": "Настройка границ смешивания рта. Больше — оригинальный рот, меньше — свапнутый.",
        "Adjust the final blend value.": "Настройка финального смешивания.",
        "Adjust the size of the Mask. Mast the entire face.": "Настройка размера маски. Покрывает всё лицо.",
        "Adjust the size of the Mask. Mast the eyeglasses.": "Настройка размера маски. Покрывает очки.",
        "Adjust the size of the Mask. Mast the hair.": "Настройка размера маски. Покрывает волосы.",
        "Adjust the size of the Mask. Mast the inside of the mouth, including the tongue.": "Настройка размера маски. Покрывает внутреннюю часть рта, включая язык.",
        "Adjust the size of the Mask. Mast the left eye.": "Настройка размера маски. Покрывает левый глаз.",
        "Adjust the size of the Mask. Mast the left eyebrow.": "Настройка размера маски. Покрывает левую бровь.",
        "Adjust the size of the Mask. Mast the lower lip.": "Настройка размера маски. Покрывает нижнюю губу.",
        "Adjust the size of the Mask. Mast the neck.": "Настройка размера маски. Покрывает шею.",
        "Adjust the size of the Mask. Mast the nose.": "Настройка размера маски. Покрывает нос.",
        "Adjust the size of the Mask. Mast the right eye.": "Настройка размера маски. Покрывает правый глаз.",
        "Adjust the size of the Mask. Mast the right eyebrow.": "Настройка размера маски. Покрывает правую бровь.",
        "Adjust the size of the Mask. Mast the upper lip.": "Настройка размера маски. Покрывает верхнюю губу.",
        "Allow objects occluding the face to show up in the swapped image.": "Позволяет объектам, перекрывающим лицо, оставаться видимыми на свапнутом изображении.",
        "Allow some of the original face to show in the swapped result when the difference between the two images is small. Can help bring back some texture to the swapped face.": "Оставляет часть оригинального лица при малой разнице между изображениями. Может вернуть текстуру свапнутому лицу.",
        "Allow the unprocessed background from the orginal image to show in the final swap.": "Оставляет необработанный фон из исходного изображения в финальном результате.",
        "Apply JPEG Compression to the swapped face to make output more realistic": "Применяет сжатие JPEG к свапнутому лицу для реалистичности",
        "Apply additional swapping iterations to increase the strength of the result, which may increase likeness.": "Дополнительные итерации свапа для усиления результата и схожести.",
        "Blend at the end of pipeline.": "Смешивание в конце пайплайна.",
        "Blend differecing value.": "Степень разностного смешивания.",
        "Blend the value for Background Parser": "Степень смешивания для фонового парсера",
        "Blend the value for Face Parser": "Степень смешивания для парсера лица",
        "Blend the value: 0.0 represents the original color, 1.0 represents the full target color.": "Степень смешивания: 0.0 — оригинальный цвет, 1.0 — целевой цвет.",
        "Blend value for Occluder and XSeg.": "Степень смешивания для Occluder и XSeg.",
        "Blue color adjustments": "Настройка синего канала",
        "Border mask blending distance.": "Дистанция смешивания границ маски.",
        "Change the Eyes Spacing distance.": "Изменяет межглазное расстояние.",
        "Changes the Brightness.": "Изменяет яркость.",
        "Changes the Contrast.": "Изменяет контраст.",
        "Changes the Gamma.": "Изменяет гамму.",
        "Changes the Hue.": "Изменяет оттенок.",
        "Changes the Saturation.": "Изменяет насыщенность.",
        "Changes the Sharpness.": "Изменяет резкость.",
        "Choose which swapper model to use for face swapping.": "Выберите модель сваппера для замены лица.",
        "Combined masks blending distance. It is not applied to the border masks.": "Дистанция смешивания объединённых масок. Не применяется к граничным маскам.",
        "Determines the factor of likeness between the source and assigned faces.": "Определяет степень схожести исходного и назначенного лиц.",
        "Enable AutoColor Transfer: 1. Hans Test without mask, 2. Hans Test with mask, 3. DFL Method without mask, 4. DFL Original Method.": "Включить перенос AutoColor: 1. Hans Test без маски, 2. Hans Test с маской, 3. DFL без маски, 4. DFL Original.",
        "Enable hair makeup": "Включить макияж волос",
        "Enable lips makeup": "Включить макияж губ",
        "Fine-tune the RGB color values of the swap.": "Точная настройка RGB-значений свапа.",
        "Green color adjustments": "Настройка зелёного канала",
        "Grows and shrinks the detection point distances.": "Увеличивает и уменьшает расстояния между точками детекции.",
        "Grows and shrinks the entire face.": "Увеличивает и уменьшает всё лицо.",
        "Grows or shrinks the occluded region": "Увеличивает или уменьшает область окклюзии",
        "Grows or shrinks the occluded region.": "Увеличивает или уменьшает область окклюзии.",
        "Higher values relaxes the similarity constraint.": "Большие значения ослабляют ограничение схожести.",
        "Increase this to show more of the swapped Mouth. Decrease it to show more of the original Mouth.": "Больше — видно больше свапнутого рта, меньше — оригинального.",
        "Increase this to show more of the swapped eyes. Decrease it to show more of the original eyes.": "Больше — видно больше свапнутых глаз, меньше — оригинальных.",
        "Increase this when swapping faces zoomed out of the frame.": "Увеличьте, если лица в кадре мелкие (сильно удалены).",
        "Increase to strengthen the effect.": "Увеличьте для усиления эффекта.",
        "Increase up to 5x additional swaps (500%). 200% is generally a good result. Set to 0 to turn off swapping but allow the rest of the pipeline to apply to the original image.": "Дополнительные свапы до 5x (500%). Обычно 200% — хороший результат. 0 отключает свап, но остальной пайплайн применяется к оригиналу.",
        "Moves the Eyes Mask on the X Axis.": "Смещает маску глаз по оси X.",
        "Moves the Eyes Mask on the Y Axis.": "Смещает маску глаз по оси Y.",
        "Moves the Mouth Mask on the X Axis.": "Смещает маску рта по оси X.",
        "Moves the Mouth Mask on the Y Axis.": "Смещает маску рта по оси Y.",
        "Negative/Positive values shrink and grow the mask.": "Отрицательные/положительные значения уменьшают и увеличивают маску.",
        "RCT Color Transfer for DFM Models": "Перенос цвета RCT для DFM-моделей",
        "Red color adjustments": "Настройка красного канала",
        "Reduce this when swapping faces zoomed out of the frame.": "Уменьшите, если лица в кадре мелкие (сильно удалены).",
        "Restore eyes from the original face.": "Восстанавливает глаза из оригинального лица.",
        "Restore mouth from the original face.": "Восстанавливает рот из оригинального лица.",
        "Select the AutoColor transfer method type. Hans Method could have some artefacts sometimes.": "Выберите метод переноса AutoColor. Метод Hans иногда даёт артефакты.",
        "Select the resolution for the swapped face in pixels. Higher values offer better quality but are slower to process.": "Разрешение свапнутого лица в пикселях. Выше — лучше качество, но медленнее.",
        "Select which pretrained DeepFaceLive (DFM) Model to use for swapping.": "Выберите предобученную модель DeepFaceLive (DFM) для свапа.",
        "Set the similarity threshold to control how similar the detected face should be to the reference (target) face.": "Порог схожести: насколько найденное лицо должно совпадать с целевым.",
        "Shifts the detection points left and right.": "Смещает точки детекции влево и вправо.",
        "Shifts the detection points up and down.": "Смещает точки детекции вверх и вниз.",
        "Shifts the eye left detection point left and right.": "Смещает левую точку глаза влево/вправо.",
        "Shifts the eye left detection point up and down.": "Смещает левую точку глаза вверх/вниз.",
        "Shifts the eye right detection point left and right.": "Смещает правую точку глаза влево/вправо.",
        "Shifts the eye right detection point up and down.": "Смещает правую точку глаза вверх/вниз.",
        "Shifts the mouth Right detection point left and right.": "Смещает правую точку рта влево/вправо.",
        "Shifts the mouth Right detection point up and down.": "Смещает правую точку рта вверх/вниз.",
        "Shifts the mouth left detection point left and right.": "Смещает левую точку рта влево/вправо.",
        "Shifts the mouth left detection point up and down.": "Смещает левую точку рта вверх/вниз.",
        "Shifts the nose detection point left and right.": "Смещает точку носа влево/вправо.",
        "Shifts the nose detection point up and down.": "Смещает точку носа вверх/вниз.",
        "These parameters determine the shape of the mask. If both are equal to 1.0, the mask will be circular. If either one is greater or less than 1.0, the mask will become oval, stretching or shrinking along the corresponding direction.": "Эти параметры задают форму маски. Если оба равны 1.0 — маска круглая; иначе овальная с растяжением/сжатием по соответствующей оси.",
        "This is a feature to perform direct adjustments to likeness of faces.": "Функция прямой настройки схожести лиц.",
        "This is an experimental feature to perform direct adjustments to the face landmarks found by the detector. There is also an option to adjust the scale of the swapped face.": "Экспериментальная функция прямой настройки ключевых точек, найденных детектором. Есть также настройка масштаба свапнутого лица.",
        "This is an experimental feature to perform direct adjustments to the position of face landmarks found by the detector.": "Экспериментальная функция прямой настройки положения ключевых точек, найденных детектором.",
        "To use, type a word(s) in the box separated by commas and press <enter>.": "Введите слово(а) через запятую и нажмите <enter>.",
        "Use descriptions to identify objects that will be present in the final swapped image.": "Используйте описания, чтобы указать объекты, которые будут в финальном изображении.",

        # Face editor help
        "Blend the value: 0.00 represents the original color, 1.00 represents the full target color.": "Степень смешивания: 0.00 — оригинальный цвет, 1.00 — целевой цвет.",
        "Blue color adjustments.": "Настройка синего канала.",
        "Blur amount.": "Степень размытия.",
        "Changes source crop scale. Increase the value to capture the face more distantly. 2.2 scale factor for cropping driving video.": "Изменяет масштаб кропа источника. Увеличьте, чтобы захватить лицо дальше. Коэффициент 2.2 для кропа ведущего видео.",
        "Changes the closing or opening of the lips.": "Изменяет закрытие/открытие губ.",
        "Changes the eyebrows direction.": "Изменяет направление бровей.",
        "Changes the head direction x-axis.": "Изменяет направление головы по оси X.",
        "Changes the head direction y-axis.": "Изменяет направление головы по оси Y.",
        "Changes the head direction z-axis.": "Изменяет направление головы по оси Z.",
        "Changes the head roll.": "Изменяет крен головы.",
        "Changes the head yaw.": "Изменяет поворот головы.",
        "Changes the horizontal eyegaze direction.": "Изменяет горизонтальное направление взгляда.",
        "Changes the mouth grin.": "Изменяет ухмылку.",
        "Changes the mouth smile.": "Изменяет улыбку.",
        "Changes the opening of the eyes.": "Изменяет открытие глаз.",
        "Changes the opening of the lips.": "Изменяет открытие губ.",
        "Changes the vertical eyegaze direction.": "Изменяет вертикальное направление взгляда.",
        "Changes the vy ratio for crop scale. Increase the value to capture the face more distantly. -0.1 factor for cropping driving video.": "Изменяет коэффициент VY для масштаба кропа. Увеличьте, чтобы захватить лицо дальше. Коэффициент -0.1 для кропа ведущего видео.",
        "Enable Face Pose/Expression Editor.": "Включить редактор позы/выражения лица.",
        "Enable eyebrows makeup.": "Включить макияж бровей.",
        "Enable face makeup. Except for hair, eyebrows, eyes and lips.": "Включить макияж лица, кроме волос, бровей, глаз и губ.",
        "Enable hair makeup.": "Включить макияж волос.",
        "Enable lips makeup.": "Включить макияж губ.",
        "Green color adjustments.": "Настройка зелёного канала.",
        "Pouting the mouth.": "Надувает губы.",
        "Pursing the mouth.": "Поджимает губы.",
        "Red color adjustments.": "Настройка красного канала.",
        "Select the target type to be edited in Face Editor.": "Выберите тип цели для редактирования в редакторе лица.",
        "Winking eye.": "Подмигивание.",

        # Dialogs / messages
        "OK": "ОК",
        "Cancel": "Отмена",
        "Yes": "Да",
        "No": "Нет",
        "Create": "Создать",
        "Create Embedding": "Создать эмбеддинг",
        "Enter embedding name": "Введите имя эмбеддинга",
        "Load Last Workspace": "Загрузить последнюю сессию",
        "About": "О программе",
        "Loading Models": "Загрузка моделей",
        "Do you want to load your last workspace?": "Загрузить последнюю сессию?",
        "Loading Models, please wait...\nDon't panic if it looks stuck!": "Загрузка моделей, подождите...\nНе паникуйте, если кажется, что зависло!",
        "Embedding Name:": "Имя эмбеддинга:",
        "Merge Type:": "Тип объединения:",
        "No parameters found in Clipboard": "Параметры не найдены в буфере обмена",
        "You need to copy parameters from any of the target face before pasting it!": "Скопируйте параметры с любого целевого лица перед вставкой!",
        "Empty Embedding Name!": "Пустое имя эмбеддинга!",
        "Embedding Name cannot be empty!": "Имя эмбеддинга не может быть пустым!",
        "Embeddings List Empty!": "Список эмбеддингов пуст!",
        "No Embeddings available to save": "Нет эмбеддингов для сохранения",
        "Markers Not Available": "Маркеры недоступны",
        "Markers can only be used for videos!": "Маркеры можно использовать только для видео!",
        "No Target Face Found": "Целевое лицо не найдено",
        "You need to have atleast one target face to create a marker": "Нужно хотя бы одно целевое лицо, чтобы создать маркер",
        "Marker Already Exists!": "Маркер уже существует!",
        "A Marker already exists for this position!": "Для этой позиции уже есть маркер!",
        "No Marker Found!": "Маркер не найден!",
        "No Marker Found for this position!": "Для этой позиции маркер не найден!",
        "No Output Folder Selected": "Папка вывода не выбрана",
        "Please select an Output folder to save the Videos before recording!": "Выберите папку вывода для сохранения видео перед записью!",
        "Please select an Output folder to save the Images/Videos before Saving/Recording!": "Выберите папку вывода для сохранения изображений/видео!",
        "FFMPEG Not Found": "FFMPEG не найден",
        "FFMPEG was not found in your system. Check your installation!": "FFMPEG не найден в системе. Проверьте установку!",
        "Invalid Frame": "Некорректный кадр",
        "Cannot save the current frame!": "Не удалось сохранить текущий кадр!",
        "No Faces Selected!": "Лица не выбраны!",
        "You need to select at least one face to create a merged embedding!": "Выберите хотя бы одно лицо для создания объединённого эмбеддинга!",
    }
}
