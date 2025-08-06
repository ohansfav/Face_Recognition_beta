# Face Recognition System - Setup Instructions

## One-Time Setup

1. Install Miniconda:
   - Download Miniconda for Windows: https://docs.conda.io/en/latest/miniconda.html
   - Run the installer
   - Choose "Just Me" when asked
   - Check "Add Miniconda3 to my PATH environment variable"

2. Open Command Prompt and run:
   ```
   conda init
   ```

3. Close and reopen Command Prompt

4. Navigate to this folder:
   ```
   cd path\to\face_recognition_folder
   ```

5. Create the environment:
   ```
   conda env create -f environment.yml
   ```

## Running the Program

1. Double-click `run.bat`
   - This will automatically activate the environment and run the program
   - If you see any error messages, follow the troubleshooting guide below

## Troubleshooting

If you get "conda is not recognized":
1. Close all Command Prompt windows
2. Open a new Command Prompt
3. Try running the program again

If you get "No module found" errors:
1. Open Command Prompt
2. Run these commands:
   ```
   conda activate face_recognition_env
   pip install face-recognition==1.3.0 face-recognition-models==0.3.0
   ```

If the camera doesn't work:
1. Make sure no other program is using the camera
2. Check Device Manager to ensure the camera is working
3. Try unplugging and plugging in the camera (if external)

## System Requirements

- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- Webcam
- About 3GB free disk space for Miniconda and environment
