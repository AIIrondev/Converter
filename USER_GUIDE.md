# Audio Format Converter - User Guide

## Introduction
Audio Format Converter is a simple yet powerful tool that helps you convert audio files between different formats. This application supports various audio formats including MP3, WAV, OGG, FLAC, and M4A.

## Key Features
- **No Command Windows**: Unlike similar converters, this application doesn't spawn annoying command prompt windows during conversion
- **Batch Conversion**: Convert multiple files at once
- **Folder Structure Preservation**: Maintains your folder organization when converting files
- **Multiple Format Support**: Convert between MP3, WAV, OGG, FLAC, M4A, and more
- **Simple Interface**: Easy-to-use graphical interface
- **Command Line Support**: For advanced users who prefer automation

## Installation

### Method 1: Using the Installer
1. Run `Install.bat`
2. Follow the on-screen instructions
3. The application will be installed to your local app data folder
4. Shortcuts will be created on your desktop and in the Start Menu

### Method 2: Portable Use
1. Simply run the `Setup_and_Run.bat` file
2. The application will download any necessary components on first run
3. All files stay in the same directory - perfect for USB drives

## Using the Application

### Graphical Interface

1. **Launch the Application**
   - Double-click on the desktop shortcut, or
   - Navigate to the installation folder and run `AudioFormatConverter.exe`

2. **Select Formats**
   - Choose your source format (the format of your original files)
   - Choose your target format (the format you want to convert to)

3. **Select Directories**
   - Click "Browse" next to "Input Directory" to select where your source files are located
   - Click "Browse" next to "Output Directory" to select where you want the converted files to be saved

4. **Check Available Files**
   - Click the "Check Folder" button to analyze the input directory
   - The application will count how many files of the selected source format are available
   - You'll see a message showing the total number of files and their combined size
   - This is useful to confirm you have the correct files before starting a conversion

5. **Conversion Options**
   - Adjust the number of conversion threads if needed (higher values may convert faster on multi-core systems)

6. **Start Conversion**
   - Click the "Convert" button to begin
   - A progress bar will show the conversion status
   - The log area will display detailed information about each file being converted

6. **Stop Conversion**
   - If needed, click "Stop" to halt the conversion process
   - Note that files already in process of being converted may still complete

### Command Line Interface

The application can also be used from the command line for automation:

```
AudioFormatConverter.exe --input "C:\Path\To\Files" --output "C:\Output\Path" --source-format mp3 --target-format wav
```

Available command-line options:
- `--input` or `-i`: Input directory containing audio files
- `--output` or `-o`: Output directory for converted files
- `--source-format` or `-sf`: Source audio format (default: mp3)
- `--target-format` or `-tf`: Target audio format (default: wav)
- `--threads` or `-t`: Number of conversion threads to use
- `--gui`: Launch the graphical interface (default if no arguments provided)

## Troubleshooting

### Common Issues

1. **"Failed to convert" messages**
   - Ensure the source file is not corrupted
   - Check that you have read/write permissions for both input and output directories
   - Try running the application as administrator

2. **"FFmpeg not found" message**
   - Run the `Setup_and_Run.bat` file which will download FFmpeg automatically
   - Ensure your internet connection is working if it's the first run

3. **Application crashes during conversion**
   - Try reducing the number of conversion threads
   - Check your system has enough available memory
   - For very large files, try converting them individually

### Resetting the Application

If you encounter persistent issues:
1. Uninstall using the uninstaller in the Start Menu
2. Delete any remaining files in the installation directory
3. Reinstall using `Install.bat`

## Support

For support, please create an issue on our GitHub repository or contact the developer.

## Credits

This application uses:
- FFmpeg (https://ffmpeg.org/) for audio conversion
- PyDub for audio processing
- Python and Tkinter for the user interface
