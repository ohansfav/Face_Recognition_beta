@echo off
echo Building Face Recognition System Executable...

:: Ensure we start in the correct directory
cd /d "%~dp0"

:: Check for Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please ensure Python is installed.
    pause
    exit /b 1
)

:: Activate conda environment
call conda activate face_recognition_env || (
    echo ERROR: Could not activate face_recognition_env
    echo Please ensure the environment is created and Conda is initialized
    pause
    exit /b 1
)

:: Install latest PyInstaller
echo Installing latest PyInstaller...
pip install --upgrade pyinstaller

:: Clean up old builds
echo Cleaning up old builds...
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
mkdir dist

:: Show current status
echo.
echo Current directory: %CD%
echo Python version:
python --version
echo PyInstaller version:
pyinstaller --version
echo.

:: Ensure all dependencies are installed
echo Installing required dependencies...
pip install -r requirements.txt

:: Build the executable
echo Building executable...
echo This may take several minutes...
pyinstaller --onefile ^
    --name "AI_Attendance_System" ^
    --add-data "*.db;." ^
    --add-data "*.txt;." ^
    --add-data "%CONDA_PREFIX%\Lib\site-packages\face_recognition_models\models;face_recognition_models/models" ^
    --hidden-import cv2 ^
    --hidden-import dlib ^
    --hidden-import face_recognition ^
    --hidden-import face_recognition.api ^
    --hidden-import face_recognition_models ^
    --hidden-import PIL ^
    --hidden-import numpy ^
    --hidden-import tkinter ^
    --hidden-import pandas ^
    --hidden-import sqlite3 ^
    --hidden-import datetime ^
    --hidden-import base64 ^
    --hidden-import database ^
    --hidden-import FR ^
    --hidden-import reports ^
    --debug all ^
    main.py > build_log.txt 2>&1

:: Display any errors or warnings from the build
echo.
echo Checking build log for errors...
findstr /I "error warning failed" build_log.txt
echo.

:: Check if build succeeded
if not exist "dist\AI_Attendance_System.exe" (
    echo.
    echo ERROR: Build failed - executable not created
    echo.
    echo Debug information:
    echo Current directory: %CD%
    dir dist
    pause
    exit /b 1
)

:: Create package folder
echo.
echo Creating distribution package...
mkdir "dist\Package"
copy "dist\AI_Attendance_System.exe" "dist\Package\"
copy "*.db" "dist\Package\"
copy "*.txt" "dist\Package\"
copy "check_environment.py" "dist\Package\"

:: Create a launcher script
echo @echo off > "dist\Package\run_attendance_system.bat"
echo python check_environment.py >> "dist\Package\run_attendance_system.bat"
echo if errorlevel 1 ( >> "dist\Package\run_attendance_system.bat"
echo     echo Environment check failed! >> "dist\Package\run_attendance_system.bat"
echo     pause >> "dist\Package\run_attendance_system.bat"
echo     exit /b 1 >> "dist\Package\run_attendance_system.bat"
echo ) >> "dist\Package\run_attendance_system.bat"
echo start /wait AI_Attendance_System.exe >> "dist\Package\run_attendance_system.bat"

:: Create ZIP file
echo Creating ZIP archive...
cd dist
powershell -Command "Compress-Archive -Force -Path 'Package\*' -DestinationPath 'AI_Attendance_System.zip'"
cd ..

echo.
echo Build complete! 
echo.
echo Files created:
dir /b dist\Package
echo.
echo Package created at: dist\AI_Attendance_System.zip
echo.
pause
