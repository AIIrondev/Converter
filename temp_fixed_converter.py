import sys
import os
import subprocess
from pathlib import Path
from pydub import AudioSegment
import argparse
import platform
import tempfile
import urllib.request
import zipfile
import concurrent.futures
from threading import Lock
import time
import shutil  # For getting terminal width and file operations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue

def download_ffmpeg_windows():
    """Download and install FFmpeg on Windows"""
    try:
        print("FFmpeg not found. Attempting to download and install...")
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        ffmpeg_zip = os.path.join(temp_dir, "ffmpeg.zip")
        ffmpeg_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "FFmpeg")
        ffmpeg_bin = os.path.join(ffmpeg_dir, "bin")
        
        # Download FFmpeg
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        print(f"Downloading FFmpeg from {url}...")
        urllib.request.urlretrieve(url, ffmpeg_zip)
        
        # Extract the zip
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted ffmpeg folder (it might have a version in the name)
        extracted_dir = None
        for item in os.listdir(temp_dir):
            if os.path.isdir(os.path.join(temp_dir, item)) and "ffmpeg" in item.lower():
                extracted_dir = os.path.join(temp_dir, item)
                break
        
        if not extracted_dir:
            print("Could not find extracted FFmpeg directory")
            return None
            
        # Move to a permanent location
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        # Copy files from bin directory to our bin directory
        bin_source = os.path.join(extracted_dir, "bin")
        if os.path.exists(bin_source):
            if os.path.exists(ffmpeg_bin):
                shutil.rmtree(ffmpeg_bin)
            shutil.copytree(bin_source, ffmpeg_bin)
            
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        
        # Check if installation succeeded
        ffmpeg_exe = os.path.join(ffmpeg_bin, "ffmpeg.exe")
        if os.path.isfile(ffmpeg_exe):
            print(f"FFmpeg successfully installed to {ffmpeg_exe}")
            return ffmpeg_exe
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
    
    return None

def find_ffmpeg():
    """Find FFmpeg executable on the system with automated installation if possible"""
    # Try to find FFmpeg in PATH
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    
    # Common installation locations based on OS
    if platform.system() == "Windows":
        common_locations = [
            r"C:\FFmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\FFmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\FFmpeg\bin\ffmpeg.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "FFmpeg", "bin", "ffmpeg.exe"),
            os.path.join(os.environ.get("APPDATA", ""), "FFmpeg", "bin", "ffmpeg.exe")
        ]
    else:  # Linux/Mac
        common_locations = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg"
        ]
    
    # Check common locations
    for location in common_locations:
        if os.path.isfile(location):
            return location
    
    # If not found and on Windows, try to download and install
    if platform.system() == "Windows":
        return download_ffmpeg_windows()
    
    return None

def find_ffprobe(ffmpeg_path=None):
    """Find ffprobe executable on the system"""
    # Try to find ffprobe in PATH
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        return ffprobe
    
    # If we have ffmpeg path, try to find ffprobe in the same directory
    if ffmpeg_path:
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe.exe" if platform.system() == "Windows" else "ffprobe")
        if os.path.isfile(ffprobe_path):
            return ffprobe_path
    
    # Common installation locations based on OS
    if platform.system() == "Windows":
        common_locations = [
            r"C:\FFmpeg\bin\ffprobe.exe",
            r"C:\Program Files\FFmpeg\bin\ffprobe.exe",
            r"C:\Program Files (x86)\FFmpeg\bin\ffprobe.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "FFmpeg", "bin", "ffprobe.exe"),
            os.path.join(os.environ.get("APPDATA", ""), "FFmpeg", "bin", "ffprobe.exe")
        ]
    else:  # Linux/Mac
        common_locations = [
            "/usr/bin/ffprobe",
            "/usr/local/bin/ffprobe",
            "/opt/local/bin/ffprobe",
            "/opt/homebrew/bin/ffprobe"
        ]
    
    # Check common locations
    for location in common_locations:
        if os.path.isfile(location):
            return location
    
    return None

def check_ffmpeg_works(ffmpeg_path):
    """Check if FFmpeg works by running a simple command"""
    if not ffmpeg_path:
        return False
    
    try:
        # Use CREATE_NO_WINDOW flag to hide console window on Windows
        CREATE_NO_WINDOW = 0x08000000
        kwargs = {}
        if platform.system() == "Windows":
            kwargs["creationflags"] = CREATE_NO_WINDOW

        subprocess.run([ffmpeg_path, "-version"], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE, 
                       timeout=5, 
                       **kwargs)
        return True
    except (subprocess.SubprocessError, OSError):
        return False

# Find FFmpeg and ffprobe executables
FFMPEG_PATH = find_ffmpeg()
FFPROBE_PATH = find_ffprobe(FFMPEG_PATH)

# Check for local FFmpeg in bin directory
script_dir = os.path.dirname(os.path.abspath(__file__))
local_ffmpeg_path = os.path.join(script_dir, "bin", "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")
local_ffprobe_path = os.path.join(script_dir, "bin", "ffprobe.exe" if platform.system() == "Windows" else "ffprobe")

if not FFMPEG_PATH and os.path.isfile(local_ffmpeg_path):
    FFMPEG_PATH = local_ffmpeg_path
    print(f"Using local FFmpeg found at: {FFMPEG_PATH}")

if not FFPROBE_PATH and os.path.isfile(local_ffprobe_path):
    FFPROBE_PATH = local_ffprobe_path
    print(f"Using local FFprobe found at: {FFPROBE_PATH}")

# Tell pydub where to find FFmpeg if we found it
if FFMPEG_PATH:
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffmpeg = FFMPEG_PATH
if FFPROBE_PATH:
    AudioSegment.ffprobe = FFPROBE_PATH

def convert_audio_file(source_path, output_path, source_format=None, target_format=None):
    """
    Convert an audio file from one format to another
    
    Args:
        source_path: Path to the source audio file
        output_path: Path where the output audio file will be saved
        source_format: Source format if not determined by file extension (optional)
        target_format: Target format if not determined by file extension (optional)
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if source file exists
        if not os.path.exists(source_path):
            print(f"File not found: {source_path}")
            return False
            
        # Define creationflags to hide command windows on Windows
        CREATE_NO_WINDOW = 0x08000000
        
        # Always use direct FFmpeg command for more reliable conversion
        # Add -hide_banner and -loglevel error to reduce unnecessary output
        cmd = [FFMPEG_PATH, "-hide_banner", "-loglevel", "error", "-i", source_path, "-y", output_path]
        
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
            # If there was an error, log it but don't display to the user
            # This keeps the logs clean while still recording issues for troubleshooting
            error_message = stderr.decode('utf-8', errors='replace').strip()
            # Only log serious errors, not just informational messages
            if error_message and ("No such file or directory" in error_message or "Error" in error_message):
                print(f"Error converting {source_path} to {output_path}")
                print(f"FFmpeg output: {error_message}")
            return False
        return True
            
    except Exception as e:
        print(f"Conversion error: {e}")
        return False

def convert_directory(input_dir, output_dir, source_format, target_format, max_workers=None):
    """
    Convert all audio files of a specified format in a directory to another format
    
    Args:
        input_dir (str): Directory containing source audio files
        output_dir (str): Directory where converted files will be saved
        source_format (str): Source audio format (e.g., "mp3", "wav")
        target_format (str): Target audio format (e.g., "mp3", "wav")
        max_workers (int, optional): Maximum number of concurrent conversion workers
    
    Returns:
        tuple: (total files converted, total files found)
    """
    # Use Path objects for better path handling
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all files with the specified source format
    source_files = list(input_path.rglob(f'*.{source_format}'))
    total_files = len(source_files)
    
    if total_files == 0:
        print(f"No {source_format.upper()} files found in the specified directory.")
        return 0, 0
    
    print(f"Found {total_files} {source_format.upper()} files. Starting conversion...")
    
    # Create output directory with the target format name
    output_dir_name = target_format.upper() + 's'  # WAVs, MP3s, etc.
    output_format_dir = output_path / output_dir_name
    output_format_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up progress tracking
    converted_files = 0
    counter_lock = Lock()  # For thread-safe counter updates
    
    # Terminal width for progress bar
    try:
        terminal_width = shutil.get_terminal_size().columns
    except (AttributeError, OSError):
        terminal_width = 80  # Default width
    
    def convert_task(source_file_path):
        nonlocal converted_files
        
        # Determine the relative path to maintain folder structure
        rel_path = source_file_path.relative_to(input_path)
        
        # Create the output path with target format directory and same structure
        target_file_dir = output_format_dir
        
        # If the file is in a subdirectory, create that structure in the output
        if rel_path.parent != Path('.'):
            target_file_dir = output_format_dir / rel_path.parent
            target_file_dir.mkdir(parents=True, exist_ok=True)
        
        # Set the output file path with new extension
        output_file_path = target_file_dir / f"{source_file_path.stem}.{target_format}"
        
        # Convert the file
        success = convert_audio_file(
            str(source_file_path), 
            str(output_file_path),
            source_format,
            target_format
        )
        
        with counter_lock:
            if success:
                nonlocal converted_files
                converted_files += 1
                
                # Calculate progress percentage
                progress = (converted_files / total_files) * 100
                bar_length = min(50, terminal_width - 30)
                filled_length = int(bar_length * converted_files // total_files)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                # Print progress
                print(f"\rProgress: [{bar}] {progress:.1f}% ({converted_files}/{total_files})", end='')
    
    # Use thread pool to convert files in parallel
    if max_workers is None:
        # Use CPU count for default parallelism
        max_workers = os.cpu_count() or 4
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit conversion tasks
        futures = [executor.submit(convert_task, source_file) for source_file in source_files]
        
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
    
    # Print final progress
    print(f"\nCompleted converting {converted_files} out of {total_files} files.")
    print(f"Output directory: {output_format_dir}")
    
    return converted_files, total_files

class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Format Converter")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Configure the main grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)  # Make log area expandable
        
        # Title
        title_label = ttk.Label(main_frame, text="Audio Format Converter", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Format selection frame
        format_frame = ttk.LabelFrame(main_frame, text="Format Selection", padding="10")
        format_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        format_frame.columnconfigure(1, weight=1)
        format_frame.columnconfigure(3, weight=1)
        
        # Source format
        ttk.Label(format_frame, text="Source Format:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.source_format = tk.StringVar(value="mp3")
        source_combo = ttk.Combobox(format_frame, textvariable=self.source_format, width=10)
        source_combo['values'] = ('mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma')
        source_combo.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Target format
        ttk.Label(format_frame, text="Target Format:").grid(row=0, column=2, sticky="w", padx=(20, 10))
        self.target_format = tk.StringVar(value="wav")
        target_combo = ttk.Combobox(format_frame, textvariable=self.target_format, width=10)
        target_combo['values'] = ('mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma')
        target_combo.grid(row=0, column=3, sticky="ew", padx=5)
        
        # Directory selection frame
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="10")
        dir_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
          # Input directory
        ttk.Label(dir_frame, text="Input Directory:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.input_dir = tk.StringVar()
        input_entry = ttk.Entry(dir_frame, textvariable=self.input_dir)
        input_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        browse_button = ttk.Button(dir_frame, text="Browse", command=self.browse_input)
        browse_button.grid(row=0, column=2, pady=5)
        # Add Check Folder button
        check_button = ttk.Button(dir_frame, text="Check Folder", command=self.check_folder)
        check_button.grid(row=0, column=3, pady=5, padx=(5, 0))
        
        # Output directory
        ttk.Label(dir_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        self.output_dir = tk.StringVar()
        output_entry = ttk.Entry(dir_frame, textvariable=self.output_dir)
        output_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Thread count
        ttk.Label(options_frame, text="Conversion Threads:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.thread_count = tk.IntVar(value=os.cpu_count() or 4)
        thread_spin = ttk.Spinbox(options_frame, from_=1, to=32, textvariable=self.thread_count, width=5)
        thread_spin.grid(row=0, column=1, sticky="w", padx=5)
          # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        
        # Convert button
        self.convert_button = ttk.Button(control_frame, text="Convert", width=15, command=self.start_conversion)
        self.convert_button.grid(row=0, column=0, padx=5, sticky="e")
        
        # Stop button (initially disabled)
        self.stop_button = ttk.Button(control_frame, text="Stop", width=15, command=self.stop_conversion, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # Log area with scrollbar
        log_frame = ttk.LabelFrame(main_frame, text="Conversion Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky="ew")
        
        # Initialize other variables
        self.conversion_thread = None
        self.conversion_running = False
        self.message_queue = queue.Queue()
        
        # Set default directories
        default_music_dir = os.path.join(os.path.expanduser("~"), "Music")
        if os.path.exists(default_music_dir):
            self.input_dir.set(default_music_dir)
            self.output_dir.set(default_music_dir)
        
        # Log welcome message
        self.log("Welcome to Audio Format Converter")
        self.log(f"Using FFmpeg at: {FFMPEG_PATH or 'Not found'}")
        self.root.after(100, self.check_queue)

    def log(self, message):
        """Add a message to the log area"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def browse_input(self):
        """Open dialog to select input directory"""
        directory = filedialog.askdirectory(
            title="Select Input Directory",
            initialdir=self.input_dir.get() or os.path.expanduser("~")
        )
        if directory:
            self.input_dir.set(directory)

    def browse_output(self):
        """Open dialog to select output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() or os.path.expanduser("~")
        )
        if directory:
            self.output_dir.set(directory)

    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        # Validate inputs
        input_dir_str = self.input_dir.get().strip()
        output_dir_str = self.output_dir.get().strip()
        source_format = self.source_format.get()
        target_format = self.target_format.get()
        
        if not input_dir_str:
            messagebox.showerror("Error", "Please select an input directory.")
            return
            
        if not output_dir_str:
            messagebox.showerror("Error", "Please select an output directory.")
            return
            
        if not os.path.isdir(input_dir_str):
            messagebox.showerror("Error", "Input directory does not exist.")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir_str, exist_ok=True)
        
        # Disable conversion button and enable stop button
        self.convert_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("Converting...")
        self.progress_var.set(0)
        self.conversion_running = True
        
        # Log start of conversion
        self.log(f"Starting conversion from {source_format.upper()} to {target_format.upper()}")
        self.log(f"Input directory: {input_dir_str}")
        self.log(f"Output directory: {output_dir_str}")
        
        # Start conversion thread
        thread_count = self.thread_count.get()
        self.conversion_thread = threading.Thread(
            target=self.conversion_worker,
            args=(input_dir_str, output_dir_str, source_format, target_format, thread_count)
        )
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def stop_conversion(self):
        """Stop the conversion process"""
        if self.conversion_running:
            self.conversion_running = False
            self.status_var.set("Stopping conversion...")
            self.log("Stopping conversion. Please wait for current tasks to finish...")

    def check_queue(self):
        """Process messages from the conversion thread"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if message[0] == "log":
                    self.log(message[1])
                elif message[0] == "progress":
                    progress_value, total = message[1], message[2]
                    if total > 0:
                        self.progress_var.set((progress_value / total) * 100)
                        self.status_var.set(f"Converting: {progress_value}/{total} files ({progress_value/total:.1%})")
                elif message[0] == "complete":
                    self.conversion_complete(message[1], message[2])
                elif message[0] == "error":
                    self.conversion_error(message[1])
                elif message[0] == "task_done":
                    # Update progress from a completed task
                    if message[1]:  # if success is True
                        progress_value = self.progress_var.get() + (100.0 / message[2]) if message[2] > 0 else 0
                        self.progress_var.set(min(progress_value, 100.0))
                
                self.message_queue.task_done()
        except queue.Empty:
            pass
        
        # Schedule next check if conversion is still running
        self.root.after(100, self.check_queue)

    def conversion_worker(self, input_dir_str, output_dir_str, source_format, target_format, max_workers):
        """Worker thread for conversion process"""
        try:
            # Use Path objects for better path handling
            input_path = Path(input_dir_str)

            # Find all files with the specified source format
            source_files = list(input_path.rglob(f'*.{source_format}'))
            total_files = len(source_files)

            if total_files == 0:
                self.message_queue.put(("log", f"No {source_format.upper()} files found in the specified directory."))
                self.message_queue.put(("complete", 0, 0))
                return

            self.message_queue.put(("log", f"Found {total_files} {source_format.upper()} files. Starting conversion..."))
            
            converted_files = 0
            
            def gui_convert_task_wrapper(item_path_str, input_root_path_str, output_base_dir_str):
                # This wrapper runs in the thread pool
                if not self.conversion_running: # Check if stop was requested
                    return False, item_path_str # Return identifier for the task

                item_path = Path(item_path_str)
                input_root_path = Path(input_root_path_str)
                file_name = item_path.name
                try:
                    # Determine the relative path to maintain folder structure
                    rel_path = item_path.relative_to(input_root_path)
                    
                    # Get source and target format
                    source_format = self.source_format.get()
                    target_format = self.target_format.get()
                    
                    # Create the output path with target format directory and same structure
                    output_dir_name = target_format.upper() + 's'  # WAVs, MP3s, etc.
                    
                    # Handle the relative path correctly - rel_path is a PurePath object
                    output_file_path = Path(output_base_dir_str) / output_dir_name
                    
                    # Add parent directories only if rel_path has a parent that is not '.'
                    if rel_path.parent and rel_path.parent != Path('.'):
                        output_file_path = output_file_path / rel_path.parent
                        
                    # Now add the filename with new extension
                    output_file_path = output_file_path / f"{item_path.stem}.{target_format}"

                    self.message_queue.put(("log", f"Converting: {file_name} from {source_format} to {target_format}"))

                    # Ensure output directory for this specific file exists
                    output_file_path.parent.mkdir(parents=True, exist_ok=True)

                    # Use CREATE_NO_WINDOW flag to hide console windows on Windows
                    CREATE_NO_WINDOW = 0x08000000
                    
                    # Define a custom conversion function that suppresses console windows
                    def convert_without_window(src, dest, src_format, tgt_format):
                        # Define parameters for FFmpeg
                        CREATE_NO_WINDOW = 0x08000000
                        
                        # Add -hide_banner and -loglevel error to reduce unnecessary output
                        cmd = [FFMPEG_PATH, "-hide_banner", "-loglevel", "error", "-i", src, "-y", dest]
                        
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
                            # Log serious errors but don't show minor warnings
                            error_message = stderr.decode('utf-8', errors='replace').strip()
                            if error_message and ("No such file or directory" in error_message or "Error" in error_message):
                                self.message_queue.put(("log", f"Error converting {os.path.basename(src)}: {error_message[:100]}..."))
                            return False
                        return True

                    # Use our custom conversion function
                    success = convert_without_window(
                        str(item_path.absolute()), 
                        str(output_file_path.absolute()),
                        source_format,
                        target_format
                    )

                    if success:
                        self.message_queue.put(("log", f"✓ Successfully converted: {file_name}"))
                    else:
                        self.message_queue.put(("log", f"✗ Failed to convert: {file_name}"))
                    return success, item_path_str
                except Exception as e:
                    self.message_queue.put(("log", f"Error processing {file_name}: {str(e)}"))
                    return False, item_path_str
                    
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for source_file_path in source_files:
                    if not self.conversion_running:
                        break # Stop submitting new tasks if stop requested
                    futures.append(executor.submit(gui_convert_task_wrapper, str(source_file_path), str(input_path), str(output_dir_str)))

                for future in concurrent.futures.as_completed(futures):
                    if not self.conversion_running: # Check again, in case stop was pressed while tasks running
                        # Attempt to cancel remaining futures (though already running tasks cannot be forcibly stopped easily)
                        for f in futures:
                            if not f.done():
                                f.cancel()
                        break
                    try:
                        success, _ = future.result() # We get (success_bool, item_path_str)
                        if success:
                            converted_files += 1
                            self.message_queue.put(("progress", converted_files, total_files))
                        self.message_queue.put(("task_done", success, total_files))
                    except concurrent.futures.CancelledError:
                        self.message_queue.put(("log", "A conversion task was cancelled."))
                    except Exception as e:
                        # Log error from the future itself, item_path_str might not be available easily here
                        self.message_queue.put(("log", f"A conversion task generated an exception: {e}"))
                        self.message_queue.put(("task_done", False, total_files))
            
            # If loop was broken due to stop_conversion
            if not self.conversion_running:
                self.message_queue.put(("log", "Conversion process was stopped by user."))
                self.message_queue.put(("complete", converted_files, total_files))
            else:
                self.message_queue.put(("complete", converted_files, total_files))
                
        except Exception as e:
            self.message_queue.put(("error", str(e)))

    def conversion_complete(self, converted_count, total_files):
        """Handle completion of conversion process"""
        self.conversion_running = False
        self.convert_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        if converted_count > 0:
            success_rate = (converted_count / total_files) * 100 if total_files > 0 else 0
            self.status_var.set(f"Conversion completed: {converted_count}/{total_files} files ({success_rate:.1f}%)")
            self.log(f"Conversion completed: {converted_count} out of {total_files} files converted successfully.")
            
            # Show completion message
            if converted_count == total_files:
                messagebox.showinfo("Conversion Complete", f"All {converted_count} files were converted successfully!")
            else:
                messagebox.showwarning("Conversion Complete", f"{converted_count} out of {total_files} files were converted successfully.")
        else:
            self.status_var.set("Conversion completed with no files converted.")
            self.log("No files were converted.")
            
            if total_files > 0:
                messagebox.showwarning("Conversion Failed", "No files were converted. Check the log for details.")

    def conversion_error(self, error_message):
        """Handle conversion error"""
        self.conversion_running = False
        self.convert_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("Conversion error")
        
        self.log(f"Error during conversion: {error_message}")
        messagebox.showerror("Conversion Error", f"An error occurred during conversion: {error_message}")

    def check_folder(self):
        """Check how many files of the selected format are in the input directory"""
        input_dir_str = self.input_dir.get().strip()
        source_format = self.source_format.get()
        
        if not input_dir_str:
            messagebox.showerror("Error", "Please select an input directory.")
            return
            
        if not os.path.isdir(input_dir_str):
            messagebox.showerror("Error", "Input directory does not exist.")
            return
        
        # Update status
        self.status_var.set(f"Scanning for {source_format.upper()} files...")
        self.root.update()
        
        try:
            # Use Path to find all files with the specified extension
            input_path = Path(input_dir_str)
            files = list(input_path.rglob(f"*.{source_format}"))
            total_files = len(files)
            
            # Calculate total size
            total_size = 0
            for file_path in files:
                total_size += file_path.stat().st_size
            
            # Convert to more readable format
            size_str = self.format_size(total_size)
            
            # Log the results
            self.log(f"Found {total_files} {source_format.upper()} files in the input directory.")
            self.log(f"Total size: {size_str}")
            
            # Show in a message box
            if total_files > 0:
                messagebox.showinfo(
                    "Folder Analysis", 
                    f"Found {total_files} {source_format.upper()} files.\n"
                    f"Total size: {size_str}\n\n"
                    f"Click 'Convert' to process these files."
                )
            else:
                messagebox.showinfo(
                    "Folder Analysis", 
                    f"No {source_format.upper()} files found in the selected directory.\n\n"
                    f"Please check that you've selected the correct source format and directory."
                )
            
            # Update status
            self.status_var.set(f"Ready - {total_files} {source_format.upper()} files found")
            
        except Exception as e:
            self.log(f"Error checking folder: {str(e)}")
            messagebox.showerror("Error", f"An error occurred while scanning the folder: {str(e)}")
            self.status_var.set("Ready")

    def format_size(self, size_bytes):
        """Format file size in bytes to a human-readable string"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def main():
    """Main function to parse arguments and run the appropriate mode"""
    parser = argparse.ArgumentParser(description='Convert audio files from one format to another.')
    parser.add_argument('-i', '--input', help='Input directory containing audio files')
    parser.add_argument('-o', '--output', help='Output directory for converted files')
    parser.add_argument('-sf', '--source-format', default='mp3', help='Source audio format (e.g., mp3, wav)')
    parser.add_argument('-tf', '--target-format', default='wav', help='Target audio format (e.g., mp3, wav)')
    parser.add_argument('-t', '--threads', type=int, help='Number of conversion threads to use')
    parser.add_argument('--gui', action='store_true', help='Launch the graphical user interface')
    
    args = parser.parse_args()
    
    # Check if FFmpeg is available
    if not FFMPEG_PATH:
        print("Error: FFmpeg executable not found. Please install FFmpeg or make sure it's in your PATH.")
        sys.exit(1)
    
    # Launch GUI if no arguments provided or --gui flag is used
    if len(sys.argv) == 1 or args.gui:
        root = tk.Tk()
        app = AudioConverterGUI(root)
        root.mainloop()
    else:
        # Command-line mode
        if not args.input or not args.output:
            parser.print_help()
            sys.exit(1)
        
        # Perform conversion
        converted, total = convert_directory(
            args.input,
            args.output,
            args.source_format,
            args.target_format,
            args.threads
        )
        
        if converted == 0 and total > 0:
            sys.exit(1)

if __name__ == "__main__":
    main()
