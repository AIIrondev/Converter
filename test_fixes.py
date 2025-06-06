import subprocess
import os
import platform
from pathlib import Path

# Define the test directory
test_dir = Path(os.path.expanduser("~")) / "Music"
if not test_dir.exists():
    test_dir = Path("c:\\Users\\Dev\\Desktop\\Neuer Ordner\\Musik")

# Test with improved error handling
def test_improved_ffmpeg():
    print("Testing improved FFmpeg error handling...")
    
    # Find a sample MP3 file
    mp3_files = list(test_dir.rglob("*.mp3"))
    if not mp3_files:
        print("No MP3 files found for testing")
        return
    
    source_file = str(mp3_files[0])
    output_file = os.path.join(os.path.dirname(source_file), "test_output.wav")
    
    print(f"Source file: {source_file}")
    print(f"Output file: {output_file}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Define FFmpeg path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(script_dir, "bin", "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")
    
    print(f"Using FFmpeg at: {ffmpeg_path}")
    
    # Define creationflags to hide command windows on Windows
    CREATE_NO_WINDOW = 0x08000000
    
    # Test with improved FFmpeg command
    print("\nTesting with improved error handling (hide_banner and error loglevel):")
    cmd = [ffmpeg_path, "-hide_banner", "-loglevel", "error", "-i", source_file, "-y", output_file]
    
    # Configure process for silent operation
    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE
    }
    
    # Add creationflags on Windows to hide console windows
    if platform.system() == "Windows":
        kwargs["creationflags"] = CREATE_NO_WINDOW
            
    # Run the conversion process
    process = subprocess.Popen(cmd, **kwargs)
    stdout, stderr = process.communicate()
    
    # Check if the conversion was successful
    if process.returncode != 0:
        # If there was an error, log it but only if it's serious
        error_message = stderr.decode('utf-8', errors='replace').strip()
        if error_message and ("No such file or directory" in error_message or "Error" in error_message):
            print(f"Error converting {source_file} to {output_file}")
            print(f"FFmpeg output: {error_message}")
        else:
            print("Conversion had non-zero return code but no serious error messages.")
            if stderr:
                print(f"FFmpeg stderr: {stderr.decode('utf-8', errors='replace')}")
    else:
        print("Conversion successful with no error messages!")
        
    # Check if the output file exists
    if os.path.exists(output_file):
        print(f"Output file successfully created: {output_file}")
    else:
        print(f"Output file was not created")

if __name__ == "__main__":
    test_improved_ffmpeg()
