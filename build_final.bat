@echo off
echo Building Face Recognition System (Debug Version)...

:: Ensure we start in the correct directory
cd /d "%~dp0"

:: Check Python and activate environment
call conda activate face_recognition_env || (
    echo ERROR: Could not activate face_recognition_env
    echo Please ensure the environment is created and Conda is initialized
    pause
    exit /b 1
)

:: Install pandas and other dependencies through conda
echo Installing dependencies through conda...
conda install -y pandas numpy pillow
conda install -y -c conda-forge face_recognition
pip install opencv-python

:: Verify installations
echo Verifying installations...
python -c "import pandas; import numpy; import cv2; import face_recognition; from PIL import Image" || (
    echo ERROR: Package verification failed
    pause
    exit /b 1
)

:: Clean previous builds
echo Cleaning previous builds...
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
mkdir dist

:: Get conda environment path
for /f "tokens=*" %%a in ('python -c "import sys; print(sys.prefix)"') do set CONDA_PREFIX=%%a

:: Copy all necessary files
echo Copying necessary files...
xcopy /E /I /Y "%CONDA_PREFIX%\Lib\site-packages\face_recognition_models\models" "dist\models"
xcopy /E /I /Y "%CONDA_PREFIX%\Library\bin\*.dll" "dist\"

:: Create the spec file for PyInstaller
echo Creating spec file...
(
echo # -*- mode: python -*-
echo import sys
echo from PyInstaller.utils.hooks import collect_data_files, collect_submodules
echo block_cipher = None
echo.
echo added_files = collect_data_files('face_recognition_models')
echo hidden_imports = collect_submodules('pandas') + collect_submodules('face_recognition')
echo.
echo a = Analysis(['main.py'],
echo     pathex=['%CD%'],
echo     binaries=[],
echo     datas=[(r'dist\models', r'face_recognition_models\models'),
echo            ('*.db', '.'),
echo            ('*.txt', '.')] + added_files,
echo     hiddenimports=hidden_imports + ['cv2', 'dlib', 'PIL._tkinter', 'PIL._imaging',
echo                    'numpy', 'pandas', 'tkinter'],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo )
echo.
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
echo.
echo exe = EXE(pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='AI_Attendance_System',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=True,
echo     disable_windowed_traceback=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo )
) > AI_Attendance_System.spec

:: Build the executable
echo Building executable...
pyinstaller --clean AI_Attendance_System.spec

:: Check if build succeeded
if not exist "dist\AI_Attendance_System.exe" (
    echo ERROR: Build failed!
    echo Check build_log.txt for details
    pause
    exit /b 1
)

:: Create a runtime environment checker
echo Creating environment checker...
(
echo import os
echo import sys
echo import importlib
echo.
echo def check_imports():
echo     required = ['pandas', 'numpy', 'cv2', 'dlib', 'face_recognition', 'PIL']
echo     for module in required:
echo         try:
echo             importlib.import_module(module^)
echo             print(f"Successfully loaded {module}")
echo         except ImportError as e:
echo             print(f"Error loading {module}: {e}")
echo             return False
echo     return True
echo.
echo if __name__ == "__main__":
echo     if not check_imports():
echo         sys.exit(1)
) > "dist\check_env.py"

:: Create a launcher batch file
echo Creating launcher...
(
echo @echo off
echo echo Checking environment...
echo python check_env.py
echo if errorlevel 1 (
echo     echo Environment check failed!
echo     pause
echo     exit /b 1
echo ^)
echo echo Starting AI Attendance System...
echo start "" "AI_Attendance_System.exe"
) > "dist\run_app.bat"

echo.
echo Build complete! 
echo.
echo To run the application:
echo 1. Go to the dist folder
echo 2. Run run_app.bat
echo.
pause
