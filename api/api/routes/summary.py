# api/routes/summary.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from database.dependencies import get_db
from api.schemas import SummaryRequest, TaskStatus
from services.transcription import generate_summary


router = APIRouter(
    prefix="/summaries",
    tags=["summaries"]
)


@router.post("/{task_id}")
async def create_summary(
        task_id: int,
        summary_request: SummaryRequest,
        background_tasks: BackgroundTasks,
        db=Depends(get_db)):
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

@router.get("/{task_id}")
async def get_summary(task_id: int, db=Depends(get_db)):
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription not completed")
    if task.summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")

    return task
