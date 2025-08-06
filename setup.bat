@echo off
:: Check if Conda is installed
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Miniconda is required but not found!
    echo Downloading Miniconda installer...
    curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
    echo Installing Miniconda...
    start /wait "" Miniconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniconda3
    del Miniconda3-latest-Windows-x86_64.exe
)

:: Create and activate conda environment
echo Creating Conda environment...
call conda env create -f environment.yml
:: Activate the environment
call conda activate face_recognition_env

echo Setting up Face Recognition System...
call conda activate face_recognition_envetting up Face Recognition System...

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.8.5 is required!
    echo Download from: https://www.python.org/downloads/release/python-385/
    pause
    exit /b 1
)

:: Create virtual environment
python -m venv .venv

:: Activate virtual environment
call .venv\Scripts\activate

:: Install packages in correct order
echo Installing required packages...

echo.
echo Step 1: Installing source packages...
pip install --no-deps wheels\dlib-19.24.0.tar.gz
pip install --no-deps wheels\face-recognition-models-0.3.0.tar.gz

echo.
echo Step 2: Installing binary wheels...
pip install --no-deps wheels\numpy-1.24.3-cp38-cp38-win_amd64.whl
pip install --no-deps wheels\face_recognition-1.3.0-py2.py3-none-any.whl
pip install --no-deps wheels\opencv_python-4.8.0.74-cp37-abi3-win_amd64.whl
pip install --no-deps wheels\Pillow-9.5.0-cp38-cp38-win_amd64.whl

echo.
echo Step 3: Installing remaining dependencies...
pip install --no-index --find-links=wheels -r requirements.txt

echo.
echo Setup complete! You can now run main.py
pause