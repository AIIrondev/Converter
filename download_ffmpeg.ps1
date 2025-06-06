# Download and extract FFmpeg binaries
$ErrorActionPreference = "Stop"

Write-Host "Downloading FFmpeg binaries..." -ForegroundColor Green

# Create bin directory if it doesn't exist
$binDir = Join-Path $PSScriptRoot "bin"
New-Item -ItemType Directory -Force -Path $binDir | Out-Null

# Download FFmpeg
$tempFile = Join-Path $env:TEMP "ffmpeg.zip"
$url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

try {
    # Use .NET WebClient for download
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($url, $tempFile)
    
    Write-Host "Download complete. Extracting..." -ForegroundColor Green
    
    # Extract only the necessary files from the zip
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($tempFile)
    
    # Find files we want (ffmpeg.exe and ffprobe.exe in bin directory)
    $entries = $zip.Entries | Where-Object { 
        $_.FullName -like "*/bin/ffmpeg.exe" -or $_.FullName -like "*/bin/ffprobe.exe" 
    }
    
    foreach ($entry in $entries) {
        $fileName = [System.IO.Path]::GetFileName($entry.FullName)
        $destinationPath = Join-Path $binDir $fileName
        
        # Extract to the bin directory
        [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $destinationPath, $true)
        Write-Host "Extracted $fileName" -ForegroundColor Green
    }
    
    $zip.Dispose()
    Remove-Item $tempFile -Force
    
    Write-Host "FFmpeg binaries successfully installed to $binDir" -ForegroundColor Green
    
} catch {
    Write-Host "Error downloading FFmpeg: $_" -ForegroundColor Red
    
    if (Test-Path $tempFile) {
        Remove-Item $tempFile -Force
    }
    
    exit 1
}
