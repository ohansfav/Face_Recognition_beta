import os
import sys
import importlib.util

def check_imports():
    required_modules = [
        'cv2',
        'dlib',
        'face_recognition',
        'PIL',
        'numpy',
        'tkinter',
        'pandas',
        'sqlite3'
    ]
    
    missing = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module} successfully imported")
        except ImportError as e:
            print(f"✗ Error importing {module}: {str(e)}")
            missing.append(module)
    return missing

def check_files():
    required_files = [
        'database.db',
        'attendance.db',
        'classes.txt'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            print(f"✗ Missing required file: {file}")
            missing.append(file)
        else:
            print(f"✓ Found required file: {file}")
    return missing

def main():
    print("Checking environment...")
    print("\nChecking imports:")
    missing_imports = check_imports()
    
    print("\nChecking required files:")
    missing_files = check_files()
    
    if missing_imports or missing_files:
        print("\nEnvironment check failed!")
        if missing_imports:
            print("\nMissing imports:")
            for module in missing_imports:
                print(f"  - {module}")
        if missing_files:
            print("\nMissing files:")
            for file in missing_files:
                print(f"  - {file}")
        sys.exit(1)
    else:
        print("\nAll environment checks passed!")

if __name__ == "__main__":
    main()
