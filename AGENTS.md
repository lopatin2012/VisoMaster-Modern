# AGENTS.md

VisoMaster-Modern: fork of VisoMaster, a PySide6 desktop app for AI face swapping and editing (images, video, webcam). No test suite, no lint/typecheck config, no CI.

## Run / setup
- Modern dev env: `.venv` on **Python 3.11** with `requirements_cu129.txt` (CUDA 12.9 / Blackwell `sm_120`). Do NOT use Python 3.14 (unsupported wheels). Setup: `py -3.11 -m venv .venv` then `.venv\Scripts\python.exe -m pip install -r requirements_cu129.txt`.
- `requirements_cu129.txt` pins torch 2.8/torchvision 0.23/torchaudio 2.8 (`+cu129`), onnxruntime-gpu 1.23.2, TensorRT 10.13 via `tensorrt-cu12*` (NOT the `tensorrt` metapackage — on Windows 10.13+ it pulls CUDA-13 wheels and fails on the deprecated `nvidia-cuda-runtime-cu13`), and PySide6 6.10.3. This is the only requirements file (the legacy CUDA 11.8/12.4 stacks were removed).
- Launch from the repo root only. Many paths are CWD-relative: `./model_assets` (`app/processors/models_data.py`), `app/ui/styles/*.qss` (`main.py`), `last_workspace.json`, `tensorrt-engines/`, `temp_output.mp4`.
- `Start.bat` launches via `.venv` (falls back to `python`), runs `convert_ui_to_py.bat`, and puts `dependencies/` + `.venv\Scripts` on PATH. `Start_Portable.bat` also prefers `.venv` but keeps `scripts/setenv.bat` for the bundled runtime. Linux: `.venv/bin/python main.py`.
- `main.py` imports `torch` before `PySide6` on purpose (PySide6 historically mutated `typing.Self`, breaking torch/torchvision). Keep that order in any new entrypoint.
- `dependencies/` is the bundled runtime (Python, CUDA, TensorRT, `ffmpeg.exe`, git-portable); `scripts/setenv.bat` prepends its paths and `main.py` auto-adds `dependencies/` to PATH. `scripts/update_cu129.bat` pulls `origin/main` (hard reset) then reinstalls requirements.
- Models are gitignored. `python download_models.py` fetches into `model_assets/` and hash-checks against `app/processors/models_data.py` (the source of truth for names/paths/hashes). DFM models go in `model_assets/dfm_models/`. Manual installs also need binaries from the visomaster-assets release copied into `dependencies/`.
- `ffmpeg` is required for video export/recording (`video_processor.create_ffmpeg_subprocess`). `main.py` auto-adds `dependencies/` to PATH, and recording picks `h264_nvenc` when the bundled ffmpeg supports it (falls back to `libx264`).

## Verify
- No tests, no headless mode. Verify changes by running the app (`.venv\Scripts\python.exe main.py` from the repo root). Do not invent test/lint commands.

## Performance / diagnostics
- `main.py --profile` (or `VISOMASTER_PROFILE=1`) enables the opt-in per-stage profiler in `app/helpers/perf.py`; it wraps model methods plus preview/display and prints averages every 60 frames and on stop. No-op when disabled.
- Measured on an RTX 5070 Ti: the TensorRT EP was **not** faster than CUDA EP for the bundled models and builds engines for minutes, so CUDA stays the default (`trt_fp16_enable` is set for opt-in TRT). Batching is not possible: Inswapper is `batch=1` and ArcFace output is fixed `(1,512)`. `h264_nvenc` is auto-selected for recording.
- Avoid per-frame `torch.cuda.empty_cache()` / `nvidia-smi` polling on hot paths (removed from the display path).

## UI / theming
- Parameter/control widgets live in `app/ui/widgets/widget_components.py` and subclass **qfluentwidgets** (`SwitchButton`, `ComboBox`, `Slider`, `LineEdit`, `ToolButton`). They must keep the legacy APIs that `layout_actions.py` and `show_hide_related_widgets` rely on: `toggled` signal, `set_value`, `reset_to_default_value`, `line_edit`, `reset_default_button`, `label_widget`, `group_layout_data`, `start_animation`.
- qfw quirks: `SwitchButton` emits `checkedChanged` (not `toggled`) and is not a `QPushButton`; `ComboBox` is `QPushButton`-based, not a `QComboBox`; all qfw constructors are `(parent=None)` and reject stray kwargs — pass `kwargs.get('parent')` explicitly.
- Theme: `app/ui/styles/fluent_theme.py` sets the qfw theme/accent. `main.py` and `control_actions.change_theme` still apply `qdarktheme` + `app/ui/styles/{dark,light}_styles.qss` for the standard Qt widgets that qfw doesn't replace (docks, tabs, lists, menus).

## Localization (i18n)
- `app/helpers/i18n.py` holds a dict-based i18n: English source strings are the keys, `tr()` looks them up for the current language, saved via `QSettings`.
- Translation is applied in three places: `main_ui` loads/applies at startup, `layout_actions` uses `i18n.set_widget_text/set_widget_tooltip` for LAYOUT_DATA labels/help/group titles, and `control_actions.change_language` re-applies live (widgets keep the English source in the `_i18n_src`/`_i18n_tip` properties so switching back works).
- Never translate dropdown `options` — they are functional values compared in code (models, `Dark/Light`, `Opal/Pearl/Optimal`, ...). Translate only `label`/`help`, `.ui` strings and user-facing messages.
- To localize a new string: wrap it with `i18n.tr(...)` (or `set_widget_text`) and add an entry to `TRANSLATIONS` in `i18n.py`. `README.ru.md` mirrors `README.md`.

## Generated UI files - do not hand-edit
- `app/ui/core/main_window.py` comes from `MainWindow.ui`, and `app/ui/core/media_rc.py` from `media.qrc`.
- Regenerate with `app/ui/core/convert_ui_to_py.bat` (`pyside6-uic` + `pyside6-rcc`, then fixes an import). `Start.bat` reruns this on every launch.
- Never read or edit `media_rc.py` (huge generated file).

## Architecture
- Entrypoint: `main.py` -> `MainWindow` in `app/ui/main_ui.py` (NOT `app/ui/core/main_window.py`, which is the generated form class).
- `app/processors/video_processor.py`: reads/displays frames with QTimers and dispatches frames to `FrameWorker` threads.
- `app/processors/workers/frame_worker.py`: per-frame pipeline.
- `app/processors/models_processor.py`: owns ONNX Runtime / TensorRT sessions plus per-task helpers (`face_detectors`, `face_swappers`, `face_restorers`, ...). Sessions are shared across worker threads; guard access with `model_lock`.
- Color convention: capture/image are BGR; frames are flipped to RGB for model work, flipped back to BGR before display and encoding.
- TensorRT is optional (guarded `try/except import`); built engine caches live in `tensorrt-engines/`.

## Adding settings
- Parameter/control widgets are generated from `LAYOUT_DATA` dicts in `app/ui/widgets/{common,swapper,settings,face_editor}_layout_data.py`, rendered by `layout_actions.add_widgets_to_tab_layout`.
- The widget name suffix selects the widget type: `...Toggle`, `...Selection`, `...Slider`/`...DecimalSlider`, `...Text`.
- Values are stored in `main_window.parameters[face_id]` (per-face) or `main_window.control` (settings tab). A new option needs a layout entry plus consumption in the processor/worker code.
- `ParametersDict` (in `app/helpers/miscellaneous.py`) falls back to `default_parameters` for missing keys, so old saved workspaces load cleanly when new settings are added; defaults come from the layout entry.

## Ignored runtime artifacts
`tensorrt-engines/`, `.thumbnails/`, `last_workspace.json`, `temp_output.mp4`, `output/`, `source_*/`, `dependencies/{Python,CUDA,TensorRT,git-portable}`. `.gitignore` also ignores broad patterns (`*.json`, `*.mp4`, `*.jpg`, `*.onnx`, `*.engine`, `*.dfm`, `*.exe`), so new data/config files are untracked unless forced.
