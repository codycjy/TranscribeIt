from pathlib import Path
import os

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

DEFAULT_PROVIDERS= ["openai", "anthropic"]
env_providers= os.getenv("AVAILABLE_PROVIDERS","")
import json

try:
    providers = json.loads(env_providers)
    if not isinstance(providers, list):
        AVAILABLE_PROVIDERS = DEFAULT_PROVIDERS
    else:
        AVAILABLE_PROVIDERS = providers
except json.JSONDecodeError:
    AVAILABLE_PROVIDERS = DEFAULT_PROVIDERS

DEFAULT_MODEL_MAP= {
    "openai": ["gpt-3.5-turbo"],
    "anthropic": ["claude-3-haiku-20240307"]
}

env_models= os.getenv("MODEL_MAP","")
try:
    models = json.loads(env_models)
    if not isinstance(models, dict):
        MODEL_MAP = DEFAULT_MODEL_MAP
    else:
        MODEL_MAP = models
except json.JSONDecodeError:
    MODEL_MAP = DEFAULT_MODEL_MAP

