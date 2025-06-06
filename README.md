# Audio Format Converter

A powerful, user-friendly tool to convert between various audio formats with support for multiple input directories and batch processing. No annoying command windows during conversion!

## ✨ Features

- **Multiple Audio Formats**: Convert between MP3, WAV, OGG, FLAC, M4A, AAC, WMA
- **Multiple Input Directories**: Select and process files from multiple folders simultaneously
- **Batch Processing**: Convert multiple files at once with parallel processing
- **Folder Structure Preservation**: Maintains your original folder organization
- **Modern GUI**: Intuitive interface with drag-and-drop-like folder management
- **Command Line Support**: Full CLI support for automation and scripting
- **Silent Operation**: No command windows or console popups during conversion
- **Progress Tracking**: Real-time progress bars and detailed conversion logs
- **FFmpeg Integration**: Automatic FFmpeg download and setup
- **Cross-Platform Ready**: Built for Windows with future cross-platform support

## 🚀 Quick Start

### Option 1: Use Pre-built Executable (Recommended)
1. Download `AudioFormatConverter.exe` from releases
2. Double-click to launch the GUI
3. Add your input folders, select formats, and convert!

### Option 2: Build from Source
1. Clone this repository
2. Run the build script:
   ```powershell
   .\build_and_run.ps1
   ```
3. The executable will be created in the `dist` folder

## 📖 How to Use

### Graphical User Interface (GUI)

1. **Launch**: Double-click `AudioFormatConverter.exe`
2. **Select Formats**: Choose source and target formats from dropdown menus
3. **Add Input Directories**: 
   - Click "Add Folder" to select directories containing your audio files
   - Add multiple directories as needed
   - Use "Remove Selected" or "Clear All" to manage your list
4. **Set Output Directory**: Click "Browse" to choose where converted files will be saved
5. **Preview**: Click "Check Folders" to see how many files will be converted
6. **Convert**: Click "Convert" to start the batch conversion process

**Pro Tips:**
- The folder structure from each input directory will be preserved in the output
- Use "Check Folders" to verify you have the right files before converting
- Adjust thread count for optimal performance on your system

### Command Line Interface (CLI)

Perfect for automation, batch scripts, and power users:

```bash
# Convert from single directory
AudioFormatConverter.exe -i "C:\Music\MP3s" -o "C:\Music\WAVs" -sf mp3 -tf wav

# Convert from multiple directories
AudioFormatConverter.exe -i "C:\Music\Album1" "C:\Music\Album2" "C:\Downloads\Audio" -o "C:\Converted" -sf flac -tf mp3

# Use custom thread count
AudioFormatConverter.exe -i "C:\Music" -o "C:\Output" -sf mp3 -tf wav -t 8
```

#### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `-i, --input` | Input directory(ies) | `-i "C:\Music" "C:\Downloads"` |
| `-o, --output` | Output directory | `-o "C:\Converted"` |
| `-sf, --source-format` | Source format | `-sf mp3` |
| `-tf, --target-format` | Target format | `-tf wav` |
| `-t, --threads` | Number of threads | `-t 4` |
| `--gui` | Launch GUI mode | `--gui` |

## 🛠️ Building from Source

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Build Process

#### Using Build Scripts (Recommended)

**Windows Batch (Simple):**
```cmd
build_and_run.bat
```

**PowerShell (Advanced):**
```powershell
# Basic build
.\build_and_run.ps1

# Clean build with verbose output
.\build_and_run.ps1 -Clean -Verbose

# Build without running
.\build_and_run.ps1 -NoRun
```

#### Manual Build
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller AudioFormatConverter.spec --clean --noconfirm
```

### Build Options

| PowerShell Parameter | Description |
|---------------------|-------------|
| `-Clean` | Remove previous build files |
| `-NoRun` | Build only, don't run |
| `-Console` | Build with console (for debugging) |
| `-Verbose` | Show detailed output |
| `-OutputDir` | Custom output directory |

## 📁 Project Structure

```
Converter/
├── audio_format_converter.py    # Main application source
├── AudioFormatConverter.spec    # PyInstaller build configuration
├── build_and_run.bat           # Windows build script
├── build_and_run.ps1           # PowerShell build script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── bin/                        # FFmpeg binaries (optional)
│   ├── ffmpeg.exe
│   └── ffprobe.exe
└── dist/                       # Built executable (after build)
    └── AudioFormatConverter.exe
```

## ⚡ Performance & Quality

- **Multi-threaded Processing**: Utilizes all CPU cores by default
- **High-Quality Conversion**: Uses FFmpeg for professional-grade audio processing
- **Memory Efficient**: Processes files in batches to handle large libraries
- **Progress Tracking**: Real-time progress bars and ETA estimates

## 🔧 Troubleshooting

### Common Issues

**"FFmpeg not found"**
- The application will automatically download FFmpeg on first run
- Ensure internet connection is available
- Manual installation: Place `ffmpeg.exe` in the `bin` folder

**"Failed to convert" errors**
- Check file permissions (read/write access)
- Ensure source files are not corrupted
- Try running as administrator
- Verify source and target formats are supported

**Application crashes**
- Reduce thread count in options
- Check available system memory
- Try converting smaller batches

**Performance optimization**
- Increase thread count on multi-core systems
- Use SSD storage for better I/O performance
- Close other applications during large conversions

### Getting Help

1. Check the conversion log for detailed error messages
2. Try the built-in "Check Folders" feature to verify your setup
3. Test with a small number of files first
4. Create an issue on GitHub with log details

## 🎵 Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| MP3 | `.mp3` | MPEG-1 Audio Layer 3 |
| WAV | `.wav` | Waveform Audio File |
| FLAC | `.flac` | Free Lossless Audio Codec |
| OGG | `.ogg` | Ogg Vorbis |
| M4A | `.m4a` | MPEG-4 Audio |
| AAC | `.aac` | Advanced Audio Coding |
| WMA | `.wma` | Windows Media Audio |

## 🏗️ Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Architecture
- **Frontend**: Tkinter GUI with modern styling
- **Backend**: Multi-threaded conversion engine
- **Audio Processing**: FFmpeg integration
- **Build System**: PyInstaller for executable generation

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🙏 Credits

- **FFmpeg**: The backbone of audio conversion (https://ffmpeg.org/)
- **Python**: Programming language and ecosystem
- **PyInstaller**: Executable packaging
- **Contributors**: Everyone who helped improve this tool

---

**Made with ❤️ for the audio conversion community**
