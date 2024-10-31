from pathlib import Path

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DATABASE_PATH = BASE_DIR / "transcriptions.db"
WHISPER_MODEL = "base"

DOWNLOAD_DIR.mkdir(exist_ok=True)

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
    'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
    'quiet': True,
    'no_warnings': True,
}
