@echo off
call scripts\setenv.bat

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" main.py
) else (
    "%PYTHON_EXECUTABLE%" main.py
)
pause
