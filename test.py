try:
    from yt_dlp import YoutubeDL
    HAS_YTDLP = True
except Exception:
    YoutubeDL = None
    HAS_YTDLP = False

try:
    from pytube import YouTube
    HAS_PYTUBE = True
except Exception:
    YouTube = None
    HAS_PYTUBE = False

import csv
import os
import re
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path

# ----------------------------------------
# Konfiguration
# ----------------------------------------
DOWNLOAD_FOLDER = Path("songs")
DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

INPUT_CSV = Path('/home/max/Dokumente/adressen.csv')
OUTPUT_CSV = Path('output.csv')

# ----------------------------------------
# Hilfsfunktionen
# ----------------------------------------

def sanitize_filename(name: str) -> str:
    """Ersetzt ungültige Dateinamen-Zeichen durch Unterstriche."""
    if not name:
        return "unknown"
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', name)
    return sanitized.strip()[:200]


def parse_input_paths(input_value: str):
    if not input_value:
        return []
    paths = [path.strip() for path in input_value.split(';') if path.strip()]
    return [Path(path) for path in paths]


def read_tracks(input_value, status_queue: queue.Queue = None):
    """Liest Trackdaten aus einer oder mehreren CSV-Dateien und gibt eine Liste von Datensätzen zurück."""
    input_paths = parse_input_paths(str(input_value))
    tracks = []

    for input_path in input_paths:
        if not input_path.exists():
            message = f"FEHLER: Die Datei '{input_path}' wurde nicht gefunden."
            if status_queue:
                status_queue.put({'type': 'status', 'text': message + '\n'})
            else:
                print(message)
            continue

        with input_path.open('r', encoding='utf-8', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                message = f"FEHLER: Keine Kopfzeile in der Datei '{input_path}' gefunden."
                if status_queue:
                    status_queue.put({'type': 'status', 'text': message + '\n'})
                else:
                    print(message)
                continue

            for row in reader:
                row['Source CSV'] = input_path.name
                tracks.append(row)

    return tracks


def build_search_query(track: dict) -> str:
    """Erstellt eine Sucheingabe aus Track-Name und Interpret."""
    track_name = track.get('Track Name') or track.get('TrackName') or track.get('Title') or ''
    artist = track.get('Artist Name(s)') or track.get('Artist Names') or track.get('Artist') or ''
    album = track.get('Album Name') or track.get('Album') or ''

    parts = [part.strip() for part in [track_name, artist, album] if part and part.strip()]
    query = ' '.join(parts)
    return query or track.get('Track URI', '').strip() or track_name


def is_youtube_url(value: str) -> bool:
    value = (value or '').strip()
    return bool(value and ('youtube.com/watch' in value or 'youtu.be/' in value))


def is_youtube_id(value: str) -> bool:
    return bool(value and re.fullmatch(r'[A-Za-z0-9_-]{11}', value.strip()))


def find_youtube_video(query: str):
    """Finde ein YouTube-Video für die Suchanfrage oder benutze eine direkte URL."""
    query = (query or '').strip()
    if not query:
        return None

    if is_youtube_url(query) or is_youtube_id(query):
        return {
            'title': query,
            'webpage_url': query if is_youtube_url(query) else f'https://www.youtube.com/watch?v={query}',
        }

    if not HAS_YTDLP:
        return None

    search_string = f'ytsearch1:{query}'
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_string, download=False)

    if not info:
        return None

    if isinstance(info, dict) and info.get('entries'):
        return info['entries'][0]

    return None


def download_with_yt_dlp(video_url: str, filename: str, download_folder: Path, cookies_file: str = None, cookies_from_browser: str = None):
    download_folder.mkdir(parents=True, exist_ok=True)
    output_template = str(download_folder / f"{filename}.%(ext)s")
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        },
        'js_runtime': 'deno',
        'sleep_interval_requests': 0.5,
        'sleep_interval': 0.5,
        'sleep_edns': True,
    }
    if cookies_file:
        ydl_opts['cookiefile'] = str(cookies_file)
    if cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = [cookies_from_browser]

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

    ext = info.get('ext') or 'm4a'
    return f"{filename}.{ext}"


def download_with_pytube(video_url: str, filename: str, download_folder: Path):
    if not HAS_PYTUBE:
        raise RuntimeError('pytube ist nicht installiert')
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    if audio_stream is None:
        raise RuntimeError('Kein Audio-Stream verfügbar')

    download_folder.mkdir(parents=True, exist_ok=True)
    audio_stream.download(output_path=str(download_folder), filename=filename)
    downloaded_filename = f"{filename}.{audio_stream.subtype}"
    return downloaded_filename, yt.title, yt.watch_url


def download_tracks(input_csv: str, output_csv: Path, download_folder: Path, status_queue: queue.Queue, cookies_file: str = None, cookies_from_browser: str = None):
    tracks = read_tracks(input_csv, status_queue=status_queue)
    if not tracks:
        status_queue.put({'type': 'status', 'text': "Keine Tracks gefunden. Bitte überprüfe die Eingabedatei.\n"})
        return

    total_tracks = len(tracks)
    status_queue.put({'type': 'progress', 'value': 0, 'total': total_tracks, 'text': f'0/{total_tracks} abgeschlossen'})

    fieldnames = []
    for row in tracks:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    extra_fields = ["Search Query", "YouTube Title", "YouTube URL", "Download Filename", "Status"]

    with output_csv.open('w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames + extra_fields)
        csv_writer.writeheader()

        for index, track in enumerate(tracks):
            track_name = track.get('Track Name') or track.get('TrackName') or track.get('Title') or ''
            query = build_search_query(track)
            status_queue.put(f"Suche und lade herunter: {query}\n")

            result_row = {**track}
            result_row.update({
                "Search Query": query,
                "YouTube Title": "",
                "YouTube URL": "",
                "Download Filename": "",
                "Status": "",
            })

            try:
                video = find_youtube_video(query)
                if not video:
                    if not HAS_YTDLP:
                        status_queue.put({'type': 'status', 'text': "❌ yt-dlp ist nicht installiert, und die Suche über pytube ist nicht verfügbar. Installiere yt-dlp mit 'pip install yt-dlp'.\n"})
                        result_row["Status"] = "yt-dlp missing"
                    else:
                        status_queue.put({'type': 'status', 'text': f"❌ Kein YouTube-Ergebnis für '{query}' gefunden.\n"})
                        result_row["Status"] = "No result"
                    csv_writer.writerow(result_row)
                    continue

                video_url = video.get('webpage_url') or video.get('url')
                if not video_url:
                    raise RuntimeError('Ungültige YouTube-URL vom Suchergebnis')

                filename = sanitize_filename(track_name or video.get('title', query))
                if HAS_YTDLP:
                    downloaded_name = download_with_yt_dlp(video_url, filename, download_folder, cookies_file=cookies_file, cookies_from_browser=cookies_from_browser)
                    result_row.update({
                        "YouTube Title": video.get('title', ''),
                        "YouTube URL": video_url,
                        "Download Filename": downloaded_name,
                        "Status": "Downloaded",
                    })
                    csv_writer.writerow(result_row)
                    status_queue.put({'type': 'status', 'text': f"✅ '{query}' erfolgreich heruntergeladen als {downloaded_name}\n"})
                else:
                    downloaded_name, title, url = download_with_pytube(video_url, filename, download_folder)
                    result_row.update({
                        "YouTube Title": title,
                        "YouTube URL": url,
                        "Download Filename": downloaded_name,
                        "Status": "Downloaded",
                    })
                    csv_writer.writerow(result_row)
                    status_queue.put({'type': 'status', 'text': f"✅ '{query}' erfolgreich heruntergeladen als {downloaded_name}\n"})

            except Exception as e:
                status_queue.put({'type': 'status', 'text': f"❌ Fehler beim Verarbeiten von '{query}': {e}\n"})
                result_row["Status"] = f"Error: {e}"
                csv_writer.writerow(result_row)

            status_queue.put({'type': 'progress', 'value': index + 1, 'total': total_tracks, 'text': f'{index + 1}/{total_tracks} abgeschlossen'})

    status_queue.put(f"✅ Fertig. Ergebnisse wurden in '{output_csv}' geschrieben.\n")


def process_queue(status_text: scrolledtext.ScrolledText, status_queue: queue.Queue, progress_bar=None, status_label=None):
    done = False
    while True:
        try:
            message = status_queue.get_nowait()
        except queue.Empty:
            break

        if isinstance(message, dict):
            msg_type = message.get('type')
            if msg_type == 'done':
                done = True
                continue
            if msg_type == 'progress':
                if progress_bar is not None:
                    progress_bar['maximum'] = message.get('total', progress_bar['maximum'])
                    progress_bar['value'] = message.get('value', 0)
                if status_label is not None:
                    status_label.config(text=message.get('text', ''))
                continue
            if msg_type == 'status':
                message = message.get('text', '')
            else:
                message = str(message)

        status_text.configure(state='normal')
        status_text.insert(tk.END, message)
        status_text.see(tk.END)
        status_text.configure(state='disabled')
    return done


def choose_input_csv(input_var: tk.StringVar):
    paths = filedialog.askopenfilenames(
        title='Wähle die Eingabe-CSV-Dateien aus',
        filetypes=[('CSV-Dateien', '*.csv'), ('Alle Dateien', '*.*')]
    )
    if paths:
        input_var.set(';'.join(paths))


def choose_cookies_file(cookies_var: tk.StringVar):
    path = filedialog.askopenfilename(
        title='Wähle die Cookies-Datei aus',
        filetypes=[('Cookie-Dateien', '*.txt *.cookies *.json'), ('Alle Dateien', '*.*')]
    )
    if path:
        cookies_var.set(path)


def choose_output_csv(output_var: tk.StringVar):
    path = filedialog.asksaveasfilename(
        title='Ausgabe-CSV-Datei speichern als',
        defaultextension='.csv',
        filetypes=[('CSV-Dateien', '*.csv'), ('Alle Dateien', '*.*')]
    )
    if path:
        output_var.set(path)


def choose_download_folder(download_var: tk.StringVar):
    path = filedialog.askdirectory(title='Wähle den Download-Ordner aus')
    if path:
        download_var.set(path)


def start_download(input_var: tk.StringVar, output_var: tk.StringVar, download_var: tk.StringVar, cookies_file_var: tk.StringVar, cookies_browser_var: tk.StringVar, status_text: scrolledtext.ScrolledText, progress_bar: ttk.Progressbar, status_label: tk.Label, run_button: tk.Button):
    input_value = input_var.get()
    output_path = Path(output_var.get())
    download_folder = Path(download_var.get())
    cookies_file = cookies_file_var.get().strip() or None
    cookies_from_browser = cookies_browser_var.get().strip() or None

    input_paths = parse_input_paths(input_value)
    if not input_paths:
        messagebox.showerror('Fehler', 'Bitte wähle mindestens eine Eingabe-CSV-Datei aus.')
        return
    if not output_path.parent.exists():
        messagebox.showerror('Fehler', 'Der Zielordner für die Ausgabe-Datei existiert nicht.')
        return
    if not download_folder.exists():
        download_folder.mkdir(parents=True, exist_ok=True)

    status_text.configure(state='normal')
    status_text.delete('1.0', tk.END)
    status_text.configure(state='disabled')

    status_queue = queue.Queue()
    run_button.config(state='disabled')

    def worker():
        try:
            download_tracks(input_value, output_path, download_folder, status_queue, cookies_file=cookies_file, cookies_from_browser=cookies_from_browser)
        finally:
            status_queue.put({'type': 'done'})

    threading.Thread(target=worker, daemon=True).start()

    def poll_queue():
        done = process_queue(status_text, status_queue, progress_bar, status_label)
        if done:
            run_button.config(state='normal')
            return
        status_text.after(100, poll_queue)

    poll_queue()


def create_gui():
    root = tk.Tk()
    root.title('YouTube Audio Downloader')
    root.geometry('700x560')
    input_var = tk.StringVar(value=str(INPUT_CSV))
    output_var = tk.StringVar(value=str(OUTPUT_CSV))
    download_var = tk.StringVar(value=str(DOWNLOAD_FOLDER))

    frame = tk.Frame(root, padx=15, pady=15)
    frame.pack(fill='both', expand=True)

    tk.Label(frame, text='Eingabe-CSV-Dateien:').grid(row=0, column=0, sticky='w')
    input_entry = tk.Entry(frame, textvariable=input_var, width=65)
    input_entry.grid(row=1, column=0, sticky='w')
    tk.Button(frame, text='Wählen', command=lambda: choose_input_csv(input_var)).grid(row=1, column=1, padx=5)

    tk.Label(frame, text='Ausgabe-CSV-Datei:').grid(row=2, column=0, sticky='w', pady=(10, 0))
    output_entry = tk.Entry(frame, textvariable=output_var, width=65)
    output_entry.grid(row=3, column=0, sticky='w')
    tk.Button(frame, text='Wählen', command=lambda: choose_output_csv(output_var)).grid(row=3, column=1, padx=5)

    tk.Label(frame, text='Download-Ordner:').grid(row=4, column=0, sticky='w', pady=(10, 0))
    download_entry = tk.Entry(frame, textvariable=download_var, width=65)
    download_entry.grid(row=5, column=0, sticky='w')
    tk.Button(frame, text='Wählen', command=lambda: choose_download_folder(download_var)).grid(row=5, column=1, padx=5)

    cookies_file_var = tk.StringVar()
    cookies_browser_var = tk.StringVar()

    tk.Label(frame, text='Cookies-Datei (optional):').grid(row=6, column=0, sticky='w', pady=(10, 0))
    cookies_entry = tk.Entry(frame, textvariable=cookies_file_var, width=50)
    cookies_entry.grid(row=7, column=0, sticky='w')
    tk.Button(frame, text='Wählen', command=lambda: choose_cookies_file(cookies_file_var)).grid(row=7, column=1, padx=5)

    tk.Label(frame, text='Browser-Cookies nutzen (optional):').grid(row=8, column=0, sticky='w', pady=(10, 0))
    browser_combo = ttk.Combobox(frame, textvariable=cookies_browser_var, values=['', 'chrome', 'firefox', 'edge', 'brave'], width=20, state='readonly')
    browser_combo.grid(row=9, column=0, sticky='w')

    progress_label = tk.Label(frame, text='Fortschritt:')
    progress_label.grid(row=10, column=0, sticky='w', pady=(15, 0))
    progress_bar = ttk.Progressbar(frame, length=520, mode='determinate')
    progress_bar.grid(row=11, column=0, columnspan=2, sticky='w', pady=(5, 0))
    status_label = tk.Label(frame, text='Bereit', anchor='w')
    status_label.grid(row=12, column=0, columnspan=2, sticky='w', pady=(5, 0))

    tk.Label(frame, text='Status:').grid(row=13, column=0, sticky='w', pady=(15, 0))
    status_text = scrolledtext.ScrolledText(frame, wrap='word', state='disabled', width=82, height=10)
    status_text.grid(row=14, column=0, columnspan=2, pady=(5, 0))

    run_button = tk.Button(frame, text='Start', width=15, command=lambda: start_download(input_var, output_var, download_var, cookies_file_var, cookies_browser_var, status_text, progress_bar, status_label, run_button))
    run_button.grid(row=15, column=0, columnspan=2, pady=(15, 0))

    root.mainloop()


if __name__ == '__main__':
    create_gui()
