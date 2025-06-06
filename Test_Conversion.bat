@echo off
echo Audio Format Converter - Test Conversion
echo =====================================
echo.

set "TEST_FOLDER=%TEMP%\AudioConverterTest"
set "TEST_FILE=%TEST_FOLDER%\test.mp3"

:: Create test folder
if not exist "%TEST_FOLDER%" mkdir "%TEST_FOLDER%"

:: Check if we have FFmpeg to generate a test file
if not exist "%~dp0bin\ffmpeg.exe" (
    echo FFmpeg not found. Please run Setup_and_Run.bat first.
    goto END
)

:: Generate a test tone if it doesn't exist
if not exist "%TEST_FILE%" (
    echo Generating test audio file...
    "%~dp0bin\ffmpeg.exe" -f lavfi -i "sine=frequency=440:duration=5" -c:a libmp3lame -q:a 2 "%TEST_FILE%" -hide_banner -loglevel error
)

:: Run the converter in command-line mode
echo What would you like to test?
echo 1. Check folder functionality
echo 2. Full conversion (MP3 to WAV)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting application with the folder pre-selected...
    echo Try using the "Check Folder" button to see how many MP3 files are in the folder.
    echo.
    start "" "%~dp0dist\AudioFormatConverter.exe"
    
    echo We've generated a test MP3 file at: %TEST_FOLDER%
    echo.
    echo Instructions:
    echo 1. In the application, set the input directory to: %TEST_FOLDER%
    echo 2. Click the "Check Folder" button
    echo 3. You should see a message showing 1 MP3 file found

) else (
    echo.
    echo Running test conversion (MP3 to WAV)...
    "%~dp0dist\AudioFormatConverter.exe" --input "%TEST_FOLDER%" --output "%TEST_FOLDER%" --source-format mp3 --target-format wav
    
    echo.
    echo If the test was successful, you should find a test.wav file at:
    echo %TEST_FOLDER%\WAVs\
)

echo.
echo You can now try converting your own files using the GUI or command line.

:END
pause
