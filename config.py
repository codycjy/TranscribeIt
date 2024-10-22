import os
from pathlib import Path

# 基础目录配置
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DATABASE_PATH = BASE_DIR / "transcriptions.db"

# 创建下载目录（如果不存在）
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Whisper模型配置
WHISPER_MODEL = "base"

# YouTube下载器配置
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
    'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
}

# 任务状态
class TaskStatus:
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"

# 数据库表结构
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS transcriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    youtube_url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
)
"""
