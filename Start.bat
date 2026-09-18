@echo off
setlocal
SET "APP_ROOT=%~dp0"
SET "APP_ROOT=%APP_ROOT:~0,-1%"
SET "DEPENDENCIES=%APP_ROOT%\dependencies"
SET "VENV_PY=%APP_ROOT%\.venv\Scripts\python.exe"

cd /d "%APP_ROOT%"

REM Bundled binaries (ffmpeg) + venv tools (pyside6-uic / pyside6-rcc)
SET "PATH=%DEPENDENCIES%;%APP_ROOT%\.venv\Scripts;%PATH%"

REM Regenerate the generated Qt UI files
call app\ui\core\convert_ui_to_py.bat

if exist "%VENV_PY%" (
    "%VENV_PY%" main.py
) else (
    echo .venv not found - falling back to the "python" on PATH.
    python main.py
)
pause
