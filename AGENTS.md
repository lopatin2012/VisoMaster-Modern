# AGENTS.md

VisoMaster-Modern: fork of VisoMaster, a PySide6 desktop app for AI face swapping and editing (images, video, webcam). No test suite, no lint/typecheck config, no CI.

## Run / setup
- Modern dev env: `.venv` on **Python 3.11** with `requirements_cu129.txt` (CUDA 12.9 / Blackwell `sm_120`). Do NOT use Python 3.14 (unsupported wheels). Setup: `py -3.11 -m venv .venv` then `.venv\Scripts\python.exe -m pip install -r requirements_cu129.txt`.
- `requirements_cu129.txt` pins torch 2.8/torchvision 0.23/torchaudio 2.8 (`+cu129`), onnxruntime-gpu 1.23.2, TensorRT 10.13 via `tensorrt-cu12*` (NOT the `tensorrt` metapackage — on Windows 10.13+ it pulls CUDA-13 wheels and fails on the deprecated `nvidia-cuda-runtime-cu13`), and PySide6 6.10.3. `requirements_cu118.txt`/`cu124.txt` are the legacy upstream stacks.
- Launch from the repo root only. Many paths are CWD-relative: `./model_assets` (`app/processors/models_data.py`), `app/ui/styles/*.qss` (`main.py`), `last_workspace.json`, `tensorrt-engines/`, `temp_output.mp4`.
- Legacy conda setup: Python 3.10.13 env named `visomaster` + `requirements_cu124.txt`.
- `Start.bat` (conda) or `Start_Portable.bat` (bundled `dependencies/`). Linux: `python main.py`.
- `main.py` imports `torch` before `PySide6` on purpose: on Python 3.10 PySide6 mutates `typing.Self`, which breaks `torch._dynamo`/torchvision. Keep that order in any new entrypoint.
- `dependencies/` is the portable runtime (Python, CUDA, TensorRT, `ffmpeg.exe`, git-portable); `scripts/setenv.bat` prepends its paths, and `Start.bat` also adds it to PATH. `update_cu*.bat` pulls `origin/main` (hard reset) then reinstalls requirements.
- Models are gitignored. `python download_models.py` fetches into `model_assets/` and hash-checks against `app/processors/models_data.py` (the source of truth for names/paths/hashes). DFM models go in `model_assets/dfm_models/`. Manual installs also need binaries from the visomaster-assets release copied into `dependencies/`.
- `ffmpeg` must be on PATH for video export/recording (`video_processor.create_ffmpeg_subprocess`); the portable `dependencies/ffmpeg.exe` covers this when launched via the bat files.

## Verify
- No tests, no headless mode. Verify changes by running the app (`.venv\Scripts\python.exe main.py` from the repo root). Do not invent test/lint commands.

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
