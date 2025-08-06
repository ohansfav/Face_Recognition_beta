@echo off
echo Building Face Recognition System (Debug Version)...

:: Ensure we start in the correct directory
cd /d "%~dp0"

:: Activate conda environment
call conda activate face_recognition_env || (
    echo ERROR: Could not activate face_recognition_env
    echo Please ensure the environment is created and Conda is initialized
    pause
    exit /b 1
)

:: Check if dlib is installed and working
python -c "import dlib" || (
    echo ERROR: dlib is not working properly
    echo Please ensure dlib is properly installed in your environment
    pause
    exit /b 1
)

:: Install PyInstaller
echo Installing PyInstaller...
pip install --upgrade pyinstaller

:: Fix numpy MKL dependencies
echo Fixing numpy MKL dependencies...
python numpy_fix.py

:: Clean previous builds
echo Cleaning previous builds...
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
mkdir dist

:: Get conda environment path and copy face recognition models
echo Copying face recognition models...
for /f "tokens=*" %%a in ('python -c "import sys; print(sys.prefix)"') do set CONDA_PREFIX=%%a
mkdir "dist\models"
xcopy /E /I /Y "%CONDA_PREFIX%\Lib\site-packages\face_recognition_models\models" "dist\models"

:: Copy existing dlib files
echo Copying dlib files from working environment...
for /f "tokens=*" %%a in ('python -c "import dlib; print(dlib.__file__)"') do set DLIB_PATH=%%a
set DLIB_DIR=%DLIB_PATH:~0,-11%
xcopy /E /I /Y "%DLIB_DIR%" "dist\dlib\"

:: Copy DLL files that might be needed
echo Copying necessary DLL files...
for /f "tokens=*" %%a in ('python -c "import os, sys; print(os.path.join(sys.prefix, 'Library', 'bin'))"') do set CONDA_LIB=%%a
copy "%CONDA_LIB%\*.dll" "dist\" > nul 2>&1

:: Build the executable with debug mode
echo Building executable (Debug Mode)...
echo This may take several minutes...
pyinstaller --onefile ^
    --name "AI_Attendance_System" ^
    --add-data "*.db;." ^
    --add-data "*.txt;." ^
    --add-data "dist\models;face_recognition_models\models" ^
    --add-binary "%CONDA_LIB%\*.dll;." ^
    --windowed ^
    --icon=NONE ^
    --hidden-import cv2 ^
    --hidden-import dlib ^
    --hidden-import face_recognition ^
    --hidden-import face_recognition_models ^
    --hidden-import face_recognition.api ^
    --hidden-import face_recognition_models.detection_cnn ^
    --hidden-import face_recognition_models.face_recognition_model_v1 ^
    --hidden-import face_recognition_models.pose_predictor_five_point ^
    --hidden-import face_recognition_models.pose_predictor_68_point ^
    --hidden-import PIL ^
    --hidden-import numpy ^
    --hidden-import pandas ^
    --hidden-import sqlite3 ^
    --hidden-import tkinter ^
    --hidden-import database ^
    --hidden-import FR ^
    --hidden-import reports ^
    --collect-submodules face_recognition_models ^
    --collect-data dlib ^
    --collect-data face_recognition ^
    --collect-data face_recognition_models ^
    --debug all ^
    main.py

:: Check if build succeeded
if not exist "dist\AI_Attendance_System.exe" (
    echo ERROR: Build failed!
    echo Check build_log.txt for details
    pause
    exit /b 1
)

:: Create debug launcher
echo Creating debug launcher...
(
echo @echo off
echo echo Running AI Attendance System in debug mode...
echo echo Any errors will be displayed here and saved to debug_log.txt
echo echo.
echo set PYTHONPATH=%%~dp0
echo AI_Attendance_System.exe 2^>^&1 ^| tee debug_log.txt
echo if errorlevel 1 (
echo     echo.
echo     echo Program crashed! Check debug_log.txt for details
echo     pause
echo ^)
) > "dist\run_with_debug.bat"

echo.
echo Build complete!
echo.
echo To test the application:
echo 1. Go to the dist folder
echo 2. Run run_with_debug.bat to see any error messages
echo.
pause
