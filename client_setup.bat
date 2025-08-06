@echo off
setlocal EnableDelayedExpansion

echo AI Attendance System - Client Setup
echo ==================================
echo.

:: Check if Python 3.8 is installed
python --version 2>nul | findstr /B "Python 3.8" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3.8 is required but not found!
    echo Please download Python 3.8 from: https://www.python.org/downloads/release/python-385/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Create wheels directory if it doesn't exist
if not exist wheels mkdir wheels

:: Download required wheel files if they don't exist
echo Checking and downloading required wheels...
if not exist "wheels\dlib-19.24.0-cp38-cp38-win_amd64.whl" (
    echo Downloading dlib...
    curl -L -o "wheels\dlib-19.24.0-cp38-cp38-win_amd64.whl" "https://github.com/sachadee/Face_Recognition/raw/main/wheels/dlib-19.24.0-cp38-cp38-win_amd64.whl"
)

:: Install packages in correct order with error handling
echo.
echo Installing required packages...

:: Update pip first
python -m pip install --upgrade pip

:: Install wheel package first
pip install wheel

:: Install dlib from wheel
echo Installing dlib...
pip install "wheels\dlib-19.24.0-cp38-cp38-win_amd64.whl"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dlib.
    pause
    exit /b 1
)

:: Install other dependencies
echo Installing other dependencies...
pip install numpy==1.24.3
pip install face-recognition-models==0.3.0
pip install face-recognition==1.3.0
pip install opencv-python==4.8.0.74
pip install Pillow==9.5.0
pip install pandas==2.0.3

:: Verify installation
echo.
echo Verifying installation...
python -c "import dlib; import face_recognition; import cv2; import numpy; import PIL; import pandas" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Some packages failed to install correctly.
    echo Please try running the setup again or contact support.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo You can now run the application using: python main.py
echo.
pause
