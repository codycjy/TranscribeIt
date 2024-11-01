from utils.logger import logger
from database.dependencies import get_db
from api.schemas import TaskStatus, SummaryRequest
from services.video import VideoProcessor
from ai_providers.factory import SummarizerFactory
import os


def check_model_availability(provider: str, model: str):
    api_key = os.getenv(f"{provider.upper()}_API_KEY")
    if not api_key:
        return False
    summarizer=SummarizerFactory.create_summarizer(provider=provider, api_key=api_key, model=model)
    return summarizer.is_available()


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


async def generate_summary(task_id: int, content: str, summary_request: SummaryRequest):
    db = get_db()
    try:
        # 更新状态为正在摘要
        await db.update_task_status(task_id, TaskStatus.SUMMARIZING)

        # 获取API密钥
        api_key = os.getenv(f"{summary_request.provider.upper()}_API_KEY")
        if not api_key:
            raise ValueError(
                f"API key not found for provider {summary_request.provider}")

        # 创建摘要器实例
        summarizer = SummarizerFactory.create_summarizer(
            provider=summary_request.provider,
            api_key=api_key,
            model=summary_request.model
        )

        # 生成摘要
        summary = await summarizer.summarize(
            content,
            max_length=summary_request.max_length
        )

        # 更新任务状态和摘要内容
        await db.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            summary=summary,
            summary_provider=summary_request.provider,
            summary_model=summary_request.model
        )

    except Exception as e:
        logger.error(f"Summary generation failed for task {task_id}: {e}")
        await db.update_task_status(
            task_id,
            TaskStatus.FAILED,
            error_message=f"Summary generation failed: {str(e)}"
        )
