import os
import asyncio
import yt_dlp
import whisper
from config import YTDL_OPTIONS, WHISPER_MODEL, DOWNLOAD_DIR
from utils.logger import logger


class VideoProcessor:
    @staticmethod
    async def download_video(url: str) -> tuple[str, str]:
        """Download the video"""
        def _download():
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    raise Exception("Failed to download video")
                title = info['title']
                audio_path = str(DOWNLOAD_DIR / f"{title}.mp3")
                return title, audio_path

        return await asyncio.to_thread(_download)

    @staticmethod
    async def transcribe_audio(audio_path: str) -> str:
        """Transcribe the audio file"""
        def _transcribe():
            model = whisper.load_model(WHISPER_MODEL)
            result = model.transcribe(audio_path)
            return result["text"]

        return await asyncio.to_thread(_transcribe)

    @staticmethod
    async def cleanup_file(file_path: str):
        """Clean up the downloaded file"""
        try:
            await asyncio.to_thread(os.remove, file_path)
        except Exception as e:
            logger.error("Failed to clean up file {file_path}: %s", e)


