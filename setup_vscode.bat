@echo off
echo Installing Visual Studio Code extensions...
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance

echo.
echo Setting up Python environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo.
echo Installing required packages...
echo Installing wheels...
pip install --no-index --find-links=wheels -r requirements.txt

echo.
echo Opening project in Visual Studio Code...
code Face_Recognition.code-workspace

echo.
echo Setup complete! The project will now open in VS Code.
echo To run the application, click the "Run and Debug" button (or press F5) and select "Face Recognition System"
pause
