@echo off
echo Setting up Audio Format Converter...

:: Check if FFmpeg binaries exist and have content
if exist "%~dp0bin\ffmpeg.exe" (
    for %%I in ("%~dp0bin\ffmpeg.exe") do if %%~zI GTR 1000000 (
        echo FFmpeg found. Starting application...
        goto START_APP
    )
)

echo FFmpeg not found or is incomplete. Attempting to download...
echo This may take a few minutes.

:: Create bin directory if it doesn't exist
if not exist "%~dp0bin" mkdir "%~dp0bin"

:: Download FFmpeg using PowerShell
powershell -Command "& {Add-Type -AssemblyName System.Net.Http; $client = New-Object System.Net.Http.HttpClient; $client.Timeout = [System.TimeSpan]::FromMinutes(5); $response = $client.GetAsync('https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip').Result; if($response.IsSuccessStatusCode) { $fileBytes = $response.Content.ReadAsByteArrayAsync().Result; [System.IO.File]::WriteAllBytes('%TEMP%\ffmpeg.zip', $fileBytes); Write-Host 'Download completed successfully.'; } else { Write-Host ('Download failed with status code: ' + $response.StatusCode); exit 1 } }"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to download FFmpeg. Please ensure you have internet connection and try again.
    goto END
)

:: Extract FFmpeg using PowerShell
echo Extracting FFmpeg...
powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; $zipPath = '%TEMP%\ffmpeg.zip'; try { $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath); $entries = $zip.Entries | Where-Object { $_.FullName -like '*/bin/ffmpeg.exe' -or $_.FullName -like '*/bin/ffprobe.exe' }; foreach ($entry in $entries) { $fileName = [System.IO.Path]::GetFileName($entry.FullName); $outputPath = Join-Path '%~dp0bin' $fileName; [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $outputPath, $true); Write-Host ('Extracted ' + $fileName) }; $zip.Dispose(); Remove-Item $zipPath -Force } catch { Write-Host ('Error extracting FFmpeg: ' + $_.Exception.Message); exit 1 } }"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to extract FFmpeg. Please try reinstalling the application.
    goto END
)

:START_APP
:: Start the application
start "" "%~dp0dist\AudioFormatConverter.exe"
goto END

:END
pause
