@echo off
echo Building Face Recognition System Executable...

:: Activate environment
call conda activate face_recognition_env || (
    echo Error: Please ensure face_recognition_env is created and activated
    pause
    exit /b 1
)

:: Make sure we're in the correct directory
cd /d "%~dp0"

:: Install required packages
echo Installing required packages...
pip install -r requirements.txt
conda install -y pyinstaller
pip install pyinstaller

:: Clean up previous builds
echo Cleaning up previous builds...
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
timeout /t 2 /nobreak

:: Create a simple spec file
echo Creating spec file...
(
echo # -*- mode: python -*-
echo import sys
echo from PyInstaller.utils.hooks import collect_data_files
echo.
echo a = Analysis(
echo     ['main.py'],
echo     pathex=[r'%CD%'],
echo     binaries=[],
echo     datas=[('*.db', '.'), ('*.txt', '.'), 
echo            (r'%CONDA_PREFIX%\Lib\site-packages\face_recognition_models\models', 'face_recognition_models/models/')],
echo     hiddenimports=['cv2', 'dlib', 'face_recognition', 'PIL', 'numpy', 'tkinter', 
echo                    'pandas', 'sqlite3', 'datetime', 'base64', 
echo                    'face_recognition_models', 'face_recognition.api',
echo                    'database', 'FR', 'reports'],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     noarchive=False,
echo )
echo.
echo pyz = PYZ(a.pure)
echo.
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.datas,
echo     name='AI_Attendance_System',
echo     debug=False,
echo     strip=False,
echo     upx=True,
echo     console=True,
echo     disable_windowed_traceback=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo )
) > face_recognition.spec

:: Build the executable
echo Building executable with PyInstaller...
python -m PyInstaller --clean --debug all face_recognition.spec > build_log.txt 2>&1
echo Build log saved to build_log.txt

:: Check for common error indicators in the log
findstr /I "error warning failed" build_log.txt

:: Check if exe was created
if not exist "dist\AI_Attendance_System.exe" (
    echo Error: Failed to create executable
    pause
    exit /b 1
)

:: Create distribution folder
echo Creating distribution package...
mkdir "dist\Face_Recognition_Package"
copy "dist\AI_Attendance_System.exe" "dist\Face_Recognition_Package\"
copy "*.db" "dist\Face_Recognition_Package\"
copy "*.txt" "dist\Face_Recognition_Package\"

:: Create README
echo Creating documentation...
(
echo AI Attendance System
echo ==================
echo.
echo Quick Start:
echo 1. Extract all files
echo 2. Double-click AI_Attendance_System.exe
echo 3. Default login: admin/admin
echo.
echo Requirements:
echo - Windows 10 or later
echo - Webcam
echo.
echo Note: Keep all files in the same folder!
) > "dist\Face_Recognition_Package\README.txt"

:: Create ZIP file
echo Creating ZIP package...
powershell -Command "Compress-Archive -Force -Path 'dist\Face_Recognition_Package\*' -DestinationPath 'dist\AI_Attendance_System_Setup.zip'"

echo.
echo Build process complete!
echo Package location: dist\AI_Attendance_System_Setup.zip
echo.
echo To test the application:
echo 1. Go to dist\Face_Recognition_Package
echo 2. Run AI_Attendance_System.exe
echo.
pause
