import sys
import importlib
import os

def check_import(module_name):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown version')
        print(f"✓ {module_name} ({version})")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - Error: {str(e)}")
        return False

def check_camera():
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("✗ Camera - Error: Could not open camera")
            return False
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("✗ Camera - Error: Could not read from camera")
            return False
        print("✓ Camera (working)")
        return True
    except Exception as e:
        print(f"✗ Camera - Error: {str(e)}")
        return False

def check_files():
    required_files = [
        'main.py',
        'FR.py',
        'database.py',
        'environment.yml'
    ]
    all_present = True
    print("\nChecking required files:")
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - Missing")
            all_present = False
    return all_present

def main():
    print("=== Face Recognition System Setup Check ===\n")
    print("Checking Python environment...")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    print("\nChecking required packages:")
    
    required_packages = [
        'numpy',
        'cv2',
        'dlib',
        'PIL',
        'face_recognition'
    ]
    
    all_passed = True
    for package in required_packages:
        if not check_import(package):
            all_passed = False
    
    files_ok = check_files()
    camera_ok = check_camera()
    
    print("\n=== Summary ===")
    if all_passed and files_ok and camera_ok:
        print("✓ All checks passed! The system is ready to use.")
        print("\nYou can now run the program using run.bat")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        if not all_passed:
            print("  - Missing required packages")
        if not files_ok:
            print("  - Missing required files")
        if not camera_ok:
            print("  - Camera not working")
        print("\nPlease follow the setup instructions to resolve these issues.")
    
    print("\nPress Enter to exit...")
    input()
