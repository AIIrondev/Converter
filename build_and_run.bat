@echo off
setlocal enabledelayedexpansion

:: Audio Format Converter - Build and Run Script
:: This script builds the Python application into an executable and runs it

echo ===============================================
echo   Audio Format Converter - Build and Run
echo ===============================================
echo.

:: Change to the project directory
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully.
    echo.
)

:: Check if the main Python file exists
if not exist "audio_format_converter.py" (
    echo ERROR: audio_format_converter.py not found in current directory
    echo Please make sure you're running this script from the correct location.
    pause
    exit /b 1
)

:: Create build directory if it doesn't exist
if not exist "build" mkdir build
if not exist "dist" mkdir dist

echo Building executable...
echo.

:: Build the executable using PyInstaller
if exist "AudioFormatConverter.spec" (
    echo Using existing spec file...
    python -m PyInstaller AudioFormatConverter.spec --clean --noconfirm
) else (
    echo Creating new spec file and building...
    python -m PyInstaller --onefile --windowed --name "AudioFormatConverter" ^
                --add-data "bin;bin" ^
                --icon=icon.ico ^
                --distpath "dist" ^
                --workpath "build" ^
                --specpath "." ^
                audio_format_converter.py
)

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable created at: dist\AudioFormatConverter.exe
echo.

:: Ask user if they want to run the executable
set /p run_choice="Do you want to run the executable now? (y/n): "
if /i "!run_choice!"=="y" (
    echo.
    echo Starting Audio Format Converter...
    echo.
    
    :: Check if executable exists
    if exist "dist\AudioFormatConverter.exe" (
        start "" "dist\AudioFormatConverter.exe"
        echo Executable started!
    ) else (
        echo ERROR: Executable not found at dist\AudioFormatConverter.exe
        pause
        exit /b 1
    )
) else (
    echo.
    echo Build complete. You can run the executable manually from:
    echo %CD%\dist\AudioFormatConverter.exe
)

echo.
echo Build and deployment information:
echo - Executable location: %CD%\dist\AudioFormatConverter.exe
echo - Build files location: %CD%\build\
echo - Spec file: %CD%\AudioFormatConverter.spec
echo.
echo To distribute the application, copy the entire 'dist' folder
echo or just the AudioFormatConverter.exe file to the target system.
echo.

pause
