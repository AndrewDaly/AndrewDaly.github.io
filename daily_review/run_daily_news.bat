@echo off
echo ==========================================
echo Daily News Report - Starting up...
echo ==========================================
echo.

REM Use the virtual environment Python
set PYTHON_PATH=C:\Dev\virtual_envs\venv\Scripts\python.exe
set SCRIPT_PATH=%~dp0daily_news.py

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python not found at %PYTHON_PATH%
    echo Please check your virtual environment path.
    pause
    exit /b 1
)

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Script not found at %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Run the script
echo Using Python: %PYTHON_PATH%
echo Running script: %SCRIPT_PATH%
echo.
"%PYTHON_PATH%" "%SCRIPT_PATH%"

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================
    echo Script completed with errors (exit code: %ERRORLEVEL%)
    echo ==========================================
) else (
    echo.
    echo ==========================================
    echo Script completed successfully!
    echo ==========================================
)

pause
