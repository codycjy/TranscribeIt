from fastapi import APIRouter, HTTPException, BackgroundTasks
from database.manager import DBManager
from api.schemas import TranscriptionRequest, TranscriptionResponse, SummaryRequest, TaskStatus
from services.transcription import process_video, generate_summary

router = APIRouter()
db = get_db()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks
):
    task_id = await db.create_task(request.url)
    background_tasks.add_task(process_video, task_id, str(request.url))
    return await db.get_task(task_id)


@router.get("/transcriptions/{task_id}", response_model=TranscriptionResponse)
async def get_transcription(task_id: int):
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/transcriptions/{task_id}/summarize", response_model=TranscriptionResponse)
async def create_summary(
    task_id: int,
    summary_request: SummaryRequest,
    background_tasks: BackgroundTasks
):
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Cannot summarize: transcription not completed"
        )

    background_tasks.add_task(
        generate_summary,
        task_id,
        task.content,
        summary_request
    )

    return task
