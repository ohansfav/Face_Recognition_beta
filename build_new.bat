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

:: Install all required packages
echo Installing required packages...
pip install -r requirements.txt

:: Verify installations
python -c "import pandas; import numpy; import cv2; import dlib; import face_recognition; from PIL import Image" || (
    echo ERROR: Package verification failed
    pause
    exit /b 1
)

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

:: Build the executable with debug mode
echo Building executable (Debug Mode)...
echo This may take several minutes...
pyinstaller --clean ^
    --name "AI_Attendance_System" ^
    --add-data "*.db;." ^
    --add-data "*.txt;." ^
    --add-data "dist\models;face_recognition_models\models" ^
    --hidden-import pandas ^
    --hidden-import numpy ^
    --hidden-import cv2 ^
    --hidden-import dlib ^
    --hidden-import face_recognition ^
    --hidden-import PIL ^
    --hidden-import tkinter ^
    --collect-all pandas ^
    --collect-all numpy ^
    --collect-all face_recognition ^
    --collect-all dlib ^
    --debug all ^
    main.py

:: Check if build succeeded
if not exist "dist\AI_Attendance_System.exe" (
    echo ERROR: Build failed!
    echo Check build_log.txt for details
    pause
    exit /b 1
)

:: Create a launcher script
echo Creating launcher script...
(
echo @echo off
echo set PYTHONPATH=%%~dp0
echo AI_Attendance_System.exe
) > "dist\run_app.bat"

echo.
echo Build complete!
echo.
echo To run the application:
echo 1. Go to the dist folder
echo 2. Run run_app.bat
echo.
pause
