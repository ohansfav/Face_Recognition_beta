import os
import subprocess

def download_wheels():
    # Create wheels directory
    os.makedirs("wheels", exist_ok=True)
    import shutil
    
    # Step 1: Copy local wheels and download required packages
    print("Step 1: Setting up wheels...")
    
    try:
        # Copy dlib wheel
        print("Copying dlib wheel...")
        shutil.copy(
            r"my dlib\dlib_bin-19.24.6-cp38-cp38-win_amd64.whl",
            r"wheels\dlib-19.24.6-cp38-cp38-win_amd64.whl"
        )
        
        # Download face-recognition-models
        print("Downloading face-recognition-models...")
        models_cmd = [
            "pip", "download",
            "--no-deps",
            "-d", "wheels",
            "face-recognition-models==0.3.0"
        ]
        result = subprocess.run(models_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error downloading face-recognition-models:")
            print(result.stderr)
            return
        
        print("Successfully set up initial wheels")
    except Exception as e:
        print("Error in wheel setup:")
        print(str(e))
        return

    # Download remaining packages
    print("\nStep 2: Downloading face-recognition source...")
    face_cmd = [
        "pip", "download",
        "--no-deps",
        "--no-binary=face-recognition",
        "-d", "wheels",
        "face-recognition==1.3.0"
    ]
    result = subprocess.run(face_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error downloading face-recognition:")
        print(result.stderr)
        return

    print("\nStep 3: Downloading remaining binary wheels...")
    remaining_packages = [
        "numpy==1.24.3",
        "opencv-python==4.8.0.74",
        "Pillow==9.5.0"
    ]

    for package in remaining_packages:
        print(f"Downloading {package}...")
        cmd = [
            "pip", "download",
            "--only-binary=:all:",
            "--platform=win_amd64",
            "--python-version=38",
            "-d", "wheels",
            package
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading {package}:")
            print(result.stderr)
            return

    # Download dependencies
    print("\nStep 4: Downloading additional dependencies...")
    cmd = [
        "pip", "download",
        "--platform=win_amd64",
        "--python-version=38",
        "--only-binary=:all:",
        "-d", "wheels",
        "-r", "requirements.txt"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Note: Some dependencies may not be available as wheels, will try source distributions")
        
        # Try downloading source distributions for remaining packages
        cmd = [
            "pip", "download",
            "-d", "wheels",
            "--no-deps",
            "-r", "requirements.txt"
        ]
        subprocess.run(cmd, capture_output=True, text=True)
    
    print("\nDownload completed successfully!")

if __name__ == "__main__":
    download_wheels()