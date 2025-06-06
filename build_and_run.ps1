# Audio Format Converter - Build and Run Script (PowerShell)
# This script builds the Python application into an executable and runs it

param(
    [switch]$Clean,           # Clean build (remove previous build files)
    [switch]$NoRun,           # Build only, don't run
    [switch]$Console,         # Build with console window
    [switch]$Verbose,         # Verbose output
    [string]$OutputDir = "dist",  # Output directory
    [string]$BuildDir = "build"   # Build directory
)

# Set up error handling
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

# Function to write section headers
function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-ColorText "===============================================" "Cyan"
    Write-ColorText "  $Title" "Cyan"
    Write-ColorText "===============================================" "Cyan"
    Write-Host ""
}

# Main execution
try {
    Write-Section "Audio Format Converter - Build and Run"
    
    # Change to script directory
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $ScriptDir
    Write-ColorText "Working directory: $PWD" "Green"
    
    # Check if Python is available
    Write-ColorText "Checking Python installation..." "Yellow"
    try {
        $PythonVersion = python --version 2>&1
        Write-ColorText "Found: $PythonVersion" "Green"
    }
    catch {
        throw "Python is not installed or not in PATH. Please install Python and try again."
    }
    
    # Check if PyInstaller is installed
    Write-ColorText "Checking PyInstaller installation..." "Yellow"
    try {
        python -c "import PyInstaller; print(f'PyInstaller version: {PyInstaller.__version__}')" 2>$null
        if ($LASTEXITCODE -ne 0) { throw }
        Write-ColorText "PyInstaller is installed" "Green"
    }
    catch {
        Write-ColorText "PyInstaller not found. Installing..." "Yellow"
        pip install pyinstaller pyinstaller-hooks-contrib
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install PyInstaller"
        }
        Write-ColorText "PyInstaller installed successfully!" "Green"
    }
    
    # Check if main Python file exists
    if (-not (Test-Path "audio_format_converter.py")) {
        throw "audio_format_converter.py not found in current directory"
    }
    
    # Clean previous builds if requested
    if ($Clean) {
        Write-ColorText "Cleaning previous build files..." "Yellow"
        if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
        if (Test-Path $OutputDir) { Remove-Item $OutputDir -Recurse -Force }
        if (Test-Path "*.spec") { Remove-Item "*.spec" -Force }
        Write-ColorText "Cleanup completed" "Green"
    }
    
    # Create directories
    if (-not (Test-Path $BuildDir)) { New-Item -ItemType Directory -Path $BuildDir | Out-Null }
    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }
    
    Write-Section "Building Executable"
    
    # Check if we have an existing spec file
    $SpecFile = "AudioFormatConverter.spec"
    $UseExistingSpec = Test-Path $SpecFile
    
    if ($UseExistingSpec) {
        Write-ColorText "Using existing spec file: $SpecFile" "Green"
        
        # Build using spec file
        $BuildArgs = @(
            $SpecFile
            "--clean"
            "--noconfirm"
        )
          if ($Verbose) { $BuildArgs += "--log-level", "DEBUG" }
        
        Write-ColorText "Running: python -m PyInstaller $($BuildArgs -join ' ')" "Cyan"
        & python -m PyInstaller $BuildArgs
    }
    else {
        Write-ColorText "Creating new build configuration..." "Yellow"
        
        # Build arguments
        $BuildArgs = @(
            "--onefile"
            "--name", "AudioFormatConverter"
            "--distpath", $OutputDir
            "--workpath", $BuildDir
            "--specpath", "."
            "--clean"
            "--noconfirm"
        )
        
        # Add windowed or console mode
        if ($Console) {
            $BuildArgs += "--console"
            Write-ColorText "Building with console window" "Yellow"
        } else {
            $BuildArgs += "--windowed"
            Write-ColorText "Building as windowed application" "Yellow"
        }
        
        # Add data files if they exist
        if (Test-Path "bin") {
            $BuildArgs += "--add-data", "bin;bin"
            Write-ColorText "Including bin directory" "Green"
        }
        
        # Add icon if it exists
        if (Test-Path "icon.ico") {
            $BuildArgs += "--icon", "icon.ico"
            Write-ColorText "Using icon: icon.ico" "Green"
        }
        
        # Add verbose logging if requested
        if ($Verbose) { $BuildArgs += "--log-level", "DEBUG" }
          # Add the main Python file
        $BuildArgs += "audio_format_converter.py"
        
        Write-ColorText "Running: python -m PyInstaller $($BuildArgs -join ' ')" "Cyan"
        & python -m PyInstaller $BuildArgs
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed! Check the output above for error details."
    }
    
    Write-Section "Build Completed Successfully"
    
    # Check if executable was created
    $ExePath = Join-Path $OutputDir "AudioFormatConverter.exe"
    if (-not (Test-Path $ExePath)) {
        throw "Executable not found at expected location: $ExePath"
    }
    
    # Get file info
    $ExeInfo = Get-Item $ExePath
    $FileSizeMB = [math]::Round($ExeInfo.Length / 1MB, 2)
    
    Write-ColorText "Executable created successfully!" "Green"
    Write-ColorText "Location: $ExePath" "Green"
    Write-ColorText "Size: $FileSizeMB MB" "Green"
    Write-ColorText "Created: $($ExeInfo.CreationTime)" "Green"
    
    # Run the executable if requested
    if (-not $NoRun) {
        $RunChoice = Read-Host "`nDo you want to run the executable now? (y/n)"
        if ($RunChoice -match "^[Yy]") {
            Write-ColorText "`nStarting Audio Format Converter..." "Yellow"
            Start-Process -FilePath $ExePath
            Write-ColorText "Executable started!" "Green"
        }
    }
    
    Write-Section "Deployment Information"
    Write-ColorText "Executable location: $ExePath" "Cyan"
    Write-ColorText "Build files location: $(Join-Path $PWD $BuildDir)" "Cyan"
    Write-ColorText "Spec file: $(Join-Path $PWD $SpecFile)" "Cyan"
    Write-Host ""
    Write-ColorText "To distribute the application:" "Yellow"
    Write-ColorText "- Copy AudioFormatConverter.exe to the target system" "White"
    Write-ColorText "- No additional files or dependencies are required" "White"
    Write-ColorText "- The executable is self-contained and portable" "White"
    
}
catch {
    Write-ColorText "`nERROR: $($_.Exception.Message)" "Red"
    Write-ColorText "Build failed!" "Red"
    exit 1
}

Write-Host ""
Write-ColorText "Script completed successfully!" "Green"
