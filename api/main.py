from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
import whisper
import yt_dlp
import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path
import os
from typing import Optional, List
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
process_pool = asyncio.get_event_loop().run_in_executor(None, None)

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DATABASE_PATH = BASE_DIR / "transcriptions.db"
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
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

class TaskStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionRequest(BaseModel):
    url: HttpUrl

class TranscriptionResponse(BaseModel):
    id: int
    youtube_url: str
    title: Optional[str] = None
    content: Optional[str] = None
    status: TaskStatus
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

def init_db():
    """Initialize the SQLite database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("""
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
        """)
        conn.commit()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

class DBManager:
    @staticmethod
    async def create_task(url: str) -> int:
        def _create():
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.execute(
                "INSERT INTO transcriptions (youtube_url, status, created_at) VALUES (?, ?, ?)",
                (str(url), TaskStatus.PENDING, datetime.now())
            )
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return task_id
        return await asyncio.to_thread(_create)

    @staticmethod
    async def update_task_status(task_id: int, status: TaskStatus, title: str = None, 
                                content: str = None, error_message: str = None):
        def _update():
            conn = sqlite3.connect(DATABASE_PATH)
            update_fields = ["status = ?"]
            params = [status]
            
            if title is not None:
                update_fields.append("title = ?")
                params.append(title)
            if content is not None:
                update_fields.append("content = ?")
                params.append(content)
            if error_message is not None:
                update_fields.append("error_message = ?")
                params.append(error_message)
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                update_fields.append("completed_at = ?")
                params.append(datetime.now())
            
            params.append(task_id)
            
            query = f"UPDATE transcriptions SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()
            conn.close()
        await asyncio.to_thread(_update)

    @staticmethod
    async def get_task(task_id: int) -> Optional[TranscriptionResponse]:
        def _get():
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM transcriptions WHERE id = ?", (task_id,))
            result = cursor.fetchone()
            conn.close()
            return dict(result) if result else None

        result = await asyncio.to_thread(_get)
        return TranscriptionResponse(**result) if result else None

    @staticmethod
    async def get_all_tasks() -> List[TranscriptionResponse]:
        def _get_all():
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM transcriptions ORDER BY created_at DESC")
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]

        results = await asyncio.to_thread(_get_all)
        return [TranscriptionResponse(**row) for row in results]

class VideoProcessor:
    @staticmethod
    async def download_video(url: str) -> tuple[str, str]:
        """Async download video"""
        def _download():
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']
                audio_path = str(DOWNLOAD_DIR / f"{title}.mp3")
                return title, audio_path

        return await asyncio.to_thread(_download)

    @staticmethod
    async def transcribe_audio(audio_path: str) -> str:
        """Async transcribe audio"""
        def _transcribe():
            model = whisper.load_model(WHISPER_MODEL)
            result = model.transcribe(audio_path)
            return result["text"]

        return await asyncio.to_thread(_transcribe)

    @staticmethod
    async def cleanup_file(file_path: str):
        """Async cleanup file"""
        try:
            await asyncio.to_thread(os.remove, file_path)
        except Exception as e:
            logger.error(f"Failed to clean up file {file_path}: {e}")

async def process_video(task_id: int, url: str):
    """Main processing function"""
    try:
        # Update status to downloading
        await DBManager.update_task_status(task_id, TaskStatus.DOWNLOADING)
        
        # Download video
        title, audio_path = await VideoProcessor.download_video(url)
        
        # update status to transcribing
        await DBManager.update_task_status(task_id, TaskStatus.TRANSCRIBING, title=title)
        
        # Transcribe audio
        content = await VideoProcessor.transcribe_audio(audio_path)
        
        # Update status to completed
        await DBManager.update_task_status(
            task_id, 
            TaskStatus.COMPLETED, 
            content=content
        )
        
        # Clean up audio file # TODO: use ENV decide whether to cleanup
        await VideoProcessor.cleanup_file(audio_path)
            
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        await DBManager.update_task_status(
            task_id, 
            TaskStatus.FAILED, 
            error_message=str(e)
        )

# API endpoints
@app.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    task_id = await DBManager.create_task(request.url)
    background_tasks.add_task(process_video, task_id, str(request.url))
    return await DBManager.get_task(task_id)

@app.get("/transcriptions/{task_id}", response_model=TranscriptionResponse)
async def get_transcription(task_id: int):
    task = await DBManager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/transcriptions", response_model=List[TranscriptionResponse])
async def get_transcriptions():
    return await DBManager.get_all_tasks()

@app.delete("/transcriptions/{task_id}")
async def delete_transcription(task_id: int):
    async def _delete():
        def _del():
            conn = sqlite3.connect(DATABASE_PATH)
            conn.execute("DELETE FROM transcriptions WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
        await asyncio.to_thread(_del)
    await _delete()
    return {"message": "Task deleted"}

# Event handlers
@app.on_event("startup")
async def startup_event():
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await asyncio.to_thread(process_pool.shutdown)
