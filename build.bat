@echo off
echo Building Face Recognition System Executable...

:: Activate environment
call conda activate face_recognition_env || (
    echo Error: Please ensure face_recognition_env is created and activated
    pause
    exit /b 1
)

:: Install PyInstaller in the conda environment
conda install -y pyinstaller

:: Wait a moment for any file handles to be released
timeout /t 2 /nobreak

:: Force close any running Python processes
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul

:: Create required directories
if exist "build" rd /s /q "build"
if exist "dist" rd /s /q "dist"
mkdir build
mkdir build\AI_Attendance_System
mkdir dist
mkdir dist\AI_Attendance_System

:: Create a spec file for PyInstaller
echo Creating spec file...
(
echo # -*- mode: python -*-
echo import sys
echo from PyInstaller.utils.hooks import collect_data_files
echo.
echo block_cipher = None
echo.
echo added_files = [
echo     ('*.db', '.'),
echo     ('*.txt', '.'),
echo ]
echo.
echo a = Analysis(['main.py'],
echo              pathex=[r'%%CD%%'],
echo              binaries=[],
echo              datas=added_files,
echo              hiddenimports=['cv2', 'dlib', 'face_recognition', 'PIL', 'numpy', 'tkinter'],
echo              hookspath=[],
echo              runtime_hooks=[],
echo              excludes=[],
echo              win_no_prefer_redirects=False,
echo              win_private_assemblies=False,
echo              cipher=block_cipher,
echo              noarchive=False)
echo.
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
echo.
echo exe = EXE(pyz,
echo           a.scripts,
echo           [],
echo           exclude_binaries=True,
echo           name='AI_Attendance_System',
echo           debug=False,
echo           bootloader_ignore_signals=False,
echo           strip=False,
echo           upx=True,
echo           console=True,
echo           icon=None)
echo.
echo coll = COLLECT(exe,
echo                a.binaries,
echo                a.zipfiles,
echo                a.datas,
echo                strip=False,
echo                upx=True,
echo                upx_exclude=[],
echo                name='AI_Attendance_System')
) > build.spec

:: Build the executable
echo Building executable...
call conda run -n face_recognition_env python -m PyInstaller --clean --distpath .\dist\AI_Attendance_System --workpath .\build build.spec

:: Verify the build was successful
if not exist "dist\AI_Attendance_System\AI_Attendance_System.exe" (
    echo Error: Build failed - executable not created
    pause
    exit /b 1
)

:: Copy additional files
echo Copying additional files...
copy *.db "dist\AI_Attendance_System\" >nul
copy *.txt "dist\AI_Attendance_System\" >nul

:: Create README
echo Creating README...
(
echo AI Attendance System
echo ==================
echo.
echo Quick Start:
echo 1. Double-click "AI_Attendance_System.exe"
echo 2. The system will start automatically
echo.
echo Features:
echo - Face Recognition based attendance
echo - Automatic attendance tracking
echo - Weekly attendance reports
echo - Admin dashboard
echo.
echo Default Login:
echo Username: admin
echo Password: admin
echo.
echo Note: Make sure your webcam is connected before starting the application.
) > "dist\AI_Attendance_System\README.txt"

:: Create shortcut
echo Creating shortcut...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut($pwd.Path + '\dist\AI_Attendance_System\AI Attendance System.lnk'); $SC.TargetPath = $pwd.Path + '\dist\AI_Attendance_System\AI_Attendance_System.exe'; $SC.WorkingDirectory = $pwd.Path + '\dist\AI_Attendance_System'; $SC.Description = 'AI Attendance System'; $SC.Save()"

:: Create distribution zip
echo Creating final package...
powershell -Command "Compress-Archive -Path '.\dist\AI_Attendance_System' -DestinationPath '.\dist\AI_Attendance_System_Setup.zip' -Force"

echo.
echo Build complete! 
echo.
echo Distribution package created at: dist\AI_Attendance_System_Setup.zip
echo.
echo Instructions for clients:
echo 1. Download and extract AI_Attendance_System_Setup.zip
echo 2. Double-click "AI Attendance System" shortcut
echo 3. Default admin login: admin/admin
echo.
pause
