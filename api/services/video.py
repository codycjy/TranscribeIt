import yt_dlp
import whisper
import os
import asyncio
from config import YTDL_OPTIONS, WHISPER_MODEL, DOWNLOAD_DIR
from utils.logger import logger
from database.dependencies import get_db
from api.schemas import TaskStatus


class VideoProcessor:
    @staticmethod
    async def download_video(url: str) -> tuple[str, str]:
        """异步下载视频"""
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
        """异步转写音频"""
        def _transcribe():
            model = whisper.load_model(WHISPER_MODEL)
            result = model.transcribe(audio_path)
            return result["text"]

        return await asyncio.to_thread(_transcribe)

    @staticmethod
    async def cleanup_file(file_path: str):
        """异步清理文件"""
        try:
            await asyncio.to_thread(os.remove, file_path)
        except Exception as e:
            logger.error(f"Failed to clean up file {file_path}: {e}")


async def process_video(task_id: int, url: str):
    """处理视频转写任务的主函数"""
    db = get_db()
    try:
        # 更新状态为下载中
        await db.update_task_status(task_id, TaskStatus.DOWNLOADING)

        # 下载视频
        title, audio_path = await VideoProcessor.download_video(url)

        # 更新状态为转写中
        await db.update_task_status(task_id, TaskStatus.TRANSCRIBING, title=title)

        # 转写音频
        content = await VideoProcessor.transcribe_audio(audio_path)

        # 更新完成状态
        await db.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            content=content
        )

        # 清理文件
        await VideoProcessor.cleanup_file(audio_path)

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        await db.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error_message=str(e)
        )
