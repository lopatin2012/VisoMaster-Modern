@echo off
setlocal
set "ROOT=%~dp0.."
set "VENV_PY=%ROOT%\.venv\Scripts\python.exe"

if exist "%VENV_PY%" (
    set "PYTHON_EXECUTABLE=%VENV_PY%"
) else (
    set "PYTHON_EXECUTABLE=python"
)

git fetch origin main
git reset --hard origin/main
"%PYTHON_EXECUTABLE%" -m pip install -r requirements_cu129.txt --default-timeout 100
"%PYTHON_EXECUTABLE%" download_models.py
