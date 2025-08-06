@echo off
echo Creating minimized Conda package for Face Recognition System...

:: Create directories for package
if not exist "dist" mkdir dist
if not exist "dist\Face_Recognition" mkdir dist\Face_Recognition
if not exist "dist\Face_Recognition\dependencies" mkdir dist\Face_Recognition\dependencies

:: Download Miniconda installer (if not exists)
if not exist "dist\Face_Recognition\dependencies\Miniconda3-latest-Windows-x86_64.exe" (
    echo Downloading Miniconda installer...
    powershell -Command "Invoke-WebRequest -Uri https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -OutFile dist\Face_Recognition\dependencies\Miniconda3-latest-Windows-x86_64.exe"
)

:: Copy project files
echo Copying project files...
xcopy /Y /E /I "*.py" "dist\Face_Recognition"
xcopy /Y /E /I "*.txt" "dist\Face_Recognition"
xcopy /Y /E /I "*.db" "dist\Face_Recognition"

:: Create setup script
echo Creating setup script...
(
echo @echo off
echo echo Setting up Face Recognition System...
echo.
echo :: Check for dependencies folder
echo if not exist "dependencies\Miniconda3-latest-Windows-x86_64.exe" ^(
echo     echo Error: Missing dependencies. Please ensure you have the complete package.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo :: Install Miniconda if not present
echo where conda ^>nul 2^>^&1
echo if %%ERRORLEVEL%% NEQ 0 ^(
echo     echo Installing Miniconda...
echo     start /wait "" "dependencies\Miniconda3-latest-Windows-x86_64.exe" /InstallationType=JustMe /RegisterPython=1 /S /D=%%UserProfile%%\Miniconda3
echo     set "PATH=%%UserProfile%%\Miniconda3;%%UserProfile%%\Miniconda3\Scripts;%%UserProfile%%\Miniconda3\Library\bin;%%PATH%%"
echo ^)
echo.
echo :: Initialize conda for cmd.exe
echo call %%UserProfile%%\Miniconda3\Scripts\activate.bat
echo.
echo :: Create conda environment
echo call conda env remove --name face_recognition_env --yes 2^>nul
echo echo Creating Conda environment...
echo call conda create -n face_recognition_env -y ^
echo     python=3.8 ^
echo     dlib=19.24 ^
echo     opencv=4.8.0 ^
echo     numpy=1.24.3 ^
echo     pillow=9.5.0 ^
echo     -c conda-forge
echo.
echo :: Activate environment and install face recognition
echo call conda activate face_recognition_env
echo pip install face-recognition==1.3.0 face-recognition-models==0.3.0
echo.
echo :: Create run script
echo echo @echo off^> run.bat
echo echo call %%UserProfile%%\Miniconda3\Scripts\activate.bat^>^> run.bat
echo echo call conda activate face_recognition_env^>^> run.bat
echo echo python main.py^>^> run.bat
echo echo pause^>^> run.bat
echo.
echo echo Setup complete! 
echo echo To run the application, double-click run.bat
echo.
echo pause
) > "dist\Face_Recognition\setup.bat"

:: Create README
echo Creating README...
(
echo # Face Recognition System - Easy Setup
echo.
echo ## Installation
echo.
echo 1. Double-click `setup.bat`
echo 2. Wait for the installation to complete ^(5-10 minutes^)
echo 3. Once installation is done, use `run.bat` to start the application
echo.
echo ## System Requirements
echo.
echo * Windows 10 or later
echo * 4GB RAM minimum ^(8GB recommended^)
echo * Webcam for face detection
echo.
echo ## Troubleshooting
echo.
echo If you encounter any issues:
echo 1. Ensure your webcam is properly connected
echo 2. Make sure no other application is using the webcam
echo 3. Try running setup.bat again
) > "dist\Face_Recognition\README.md"

:: Create .gitignore
echo Creating .gitignore...
(
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
) > "dist\Face_Recognition\.gitignore"

echo.
echo Package created in dist\Face_Recognition
echo You can now distribute this folder to clients
echo.
pause
