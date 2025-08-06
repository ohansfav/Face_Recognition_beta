@echo off
setlocal EnableDelayedExpansion

:: Activate virtual environment
call .venv\Scripts\activate 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Virtual environment not found!
    echo Running initial setup...
    call client_setup.bat
    exit /b 1
)

:: Check environment
python check_environment.py
if %ERRORLEVEL% NEQ 0 (
    echo Environment check failed!
    echo Running setup to fix issues...
    call client_setup.bat
    exit /b 1
)

:: Run the main application
python main.py
pause
