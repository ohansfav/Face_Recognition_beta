import os
import pip
import shutil
import subprocess
import sys
from pip._internal.operations.freeze import freeze

def create_offline_package():
    # Create directories
    os.makedirs("offline_package", exist_ok=True)
    os.makedirs("offline_package/wheels", exist_ok=True)
    
    # Download wheels for all dependencies
    packages = [
        "dlib==19.24.0",
        "face-recognition==1.3.0",
        "opencv-python==4.8.0.74",
        "numpy==1.24.3",
        "Pillow==9.5.0"
    ]
    
    print("Downloading package wheels...")
    for package in packages:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "download",
            "--dest", 
            "offline_package/wheels",
            package
        ])
    
    # Copy your project files
    files_to_copy = [
        'main.py',
        'database.py',
        'FR.py',
        'attendance.db'
    ]
    
    for file in files_to_copy:
        shutil.copy2(file, "offline_package")
    
    # Create setup script for client
    with open("offline_package/setup.bat", "w") as f:
        f.write("""@echo off
echo Setting up AI Attendance System...

:: Create and activate virtual environment
python -m venv .venv
call .venv\\Scripts\\activate

:: Install wheels from local directory
for %%f in (wheels\\*.whl) do pip install %%f

echo Setup complete! You can now run the program.
echo To run: python main.py
pause
""")

    # Create README
    with open("offline_package/README.md", "w") as f:
        f.write("""# AI Attendance System - Offline Setup

1. Open this folder in VS Code
2. Open VS Code terminal (View > Terminal)
3. Run: setup.bat
4. After setup completes, run: python main.py

That's it! The program will start automatically.
""")
    
    # Create VS Code settings
    os.makedirs("offline_package/.vscode", exist_ok=True)
    with open("offline_package/.vscode/settings.json", "w") as f:
        f.write("""{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.defaultProfile.windows": "Command Prompt"
}""")
    
    # Create ZIP
    shutil.make_archive("AI_Attendance_System_Offline", "zip", "offline_package")
    print("\nPackage created successfully!")
    print("Location: AI_Attendance_System_Offline.zip")

if __name__ == "__main__":
    create_offline_package()