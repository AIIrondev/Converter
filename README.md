# Audio Format Converter

A simple, powerful tool to convert between various audio formats without spawning extra command windows.

## Features

- Convert between multiple audio formats (MP3, WAV, OGG, FLAC, M4A, etc.)
- Batch conversion of multiple files
- Preserves folder structure during conversion
- Simple GUI interface
- Command-line support for automation
- No annoying command windows during conversion

## Usage

### Graphical User Interface (GUI)

1. Launch the application by double-clicking the `Audio Format Converter.exe` file
2. Select the source format from the dropdown menu
3. Select the target format from the dropdown menu
4. Click "Browse" to select the input directory containing your audio files
5. Click "Browse" to select the output directory where converted files will be saved
6. Click "Convert" to start the conversion process

### Command Line Interface (CLI)

For advanced users, you can use the command line:

```
AudioFormatConverter.exe --input "C:\path\to\input\folder" --output "C:\path\to\output\folder" --source-format mp3 --target-format wav
```

#### Command Line Options

- `--input` or `-i`: Path to the input directory containing audio files
- `--output` or `-o`: Path to the output directory
- `--source-format` or `-sf`: Source audio format (e.g., mp3, wav, ogg)
- `--target-format` or `-tf`: Target audio format (e.g., mp3, wav, ogg)
- `--threads` or `-t`: Number of conversion threads to use (default: number of CPU cores)
- `--gui`: Launch the graphical user interface (default if no args provided)

## Requirements

- Windows OS (7/8/10/11)
- No additional software required (FFmpeg is included)

## Important Changes

- Fixed issue with multiple command windows appearing during conversion

## Credits

This application uses FFmpeg (https://ffmpeg.org/) for audio conversion.
