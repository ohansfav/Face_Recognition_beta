import os
import shutil

def create_package():
    # Create distribution directory
    dist_dir = "Face_Recognition_System"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    os.makedirs(os.path.join(dist_dir, ".vscode"))
    os.makedirs(os.path.join(dist_dir, "wheels"))

    # Copy project files
    files = [
        "main.py",
        "database.py",
        "FR.py",
        "attendance.db",
        "setup.bat",
        "run.bat"
    ]
    
    for file in files:
        shutil.copy2(file, dist_dir)

    # Copy wheel files
    wheel_dir = "wheels"
    for wheel in os.listdir(wheel_dir):
        shutil.copy2(
            os.path.join(wheel_dir, wheel),
            os.path.join(dist_dir, "wheels")
        )

    # Create VS Code settings
    with open(os.path.join(dist_dir, ".vscode", "settings.json"), "w") as f:
        f.write('''{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.defaultProfile.windows": "Command Prompt"
}''')

    # Create README
    with open(os.path.join(dist_dir, "README.txt"), "w") as f:
        f.write('''Face Recognition Attendance System - Quick Start

1. Install Python 3.8.5 if not installed:
   - Download from: https://www.python.org/downloads/release/python-385/
   - CHECK "Add Python to PATH" during installation

2. Open this folder in VS Code:
   - File > Open Folder
   - Select this folder

3. Open VS Code terminal:
   - View > Terminal
   - Or press: Ctrl + `

4. Run setup:
   - Type: setup.bat
   - Wait for installation to complete

5. Run the program:
   - Type: run.bat
   OR
   - Open main.py
   - Press F5

Default Login:
Username: admin
Password: admin''')

    # Create ZIP
    shutil.make_archive("Face_Recognition_System", "zip", dist_dir)
    print("Package created: Face_Recognition_System.zip")

if __name__ == "__main__":
    create_package()