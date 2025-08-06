@echo off
echo Testing Face Recognition System Setup...

:: Check for Conda
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda is not found!
    echo Please make sure Miniconda is installed and added to PATH
    pause
    exit /b 1
)

:: Print Conda version
echo Checking Conda installation...
conda --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda is not working properly
    pause
    exit /b 1
)

:: Check if environment exists
echo.
echo Checking for existing environment...
conda env list | findstr "face_recognition_env"
if %ERRORLEVEL% EQU 0 (
    echo Found existing environment, removing it...
    call conda env remove -n face_recognition_env -y
)

:: Create fresh environment
echo.
echo Creating fresh environment from environment.yml...
call conda env create -f environment.yml
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create environment
    pause
    exit /b 1
)

:: Activate environment and run check
echo.
echo Activating environment and running checks...
call conda activate face_recognition_env
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate environment
    pause
    exit /b 1
)

python check_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Setup check failed
    pause
    exit /b 1
)

echo.
echo If all checks passed, try running the main program:
echo run.bat
echo.
pause
