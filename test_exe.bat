@echo off
echo Testing AI Attendance System...
echo.

:: Check if exe exists
if not exist "dist\Package\AI_Attendance_System.exe" (
    echo ERROR: Executable not found in dist\Package folder
    pause
    exit /b 1
)

:: Create a test directory
mkdir test_run 2>nul
cd test_run

:: Copy necessary files
echo Copying files for testing...
copy ..\dist\Package\* . >nul

:: Run the executable with output logging
echo Running AI_Attendance_System.exe...
echo All output will be logged to test_output.txt
echo.
echo The program will run with full console output.
echo If it crashes, you will see the error message.
echo.
AI_Attendance_System.exe > test_output.txt 2>&1

:: Check if program crashed
if errorlevel 1 (
    echo.
    echo Program exited with an error. Here's the last few lines of output:
    echo ----------------------------------------
    for /f "skip=0 delims=" %%a in ('powershell -Command "Get-Content test_output.txt -Tail 10"') do echo %%a
    echo ----------------------------------------
)

echo.
echo Full log available in: test_run\test_output.txt
echo.
pause
