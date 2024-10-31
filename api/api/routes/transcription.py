# api/routes/transcription.py
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from api.schemas import TranscriptionRequest, TranscriptionResponse
from services.transcription import process_video
from database.dependencies import get_db

router = APIRouter(
    prefix="/transcriptions",
    tags=["transcriptions"]
)
db = get_db()


@router.post("/", response_model=TranscriptionResponse)
async def create_transcription(request: TranscriptionRequest, background_tasks: BackgroundTasks, db=Depends(get_db)):
    task_id = await db.create_task(request.url)
    background_tasks.add_task(process_video, task_id, str(request.url))
    return await db.get_task(task_id)


@router.get("/{task_id}", response_model=TranscriptionResponse)
async def get_transcription(task_id: int, db=Depends(get_db)):
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/", response_model=List[TranscriptionResponse])
async def get_transcriptions(db=Depends(get_db)):
    return await db.get_all_tasks()


@router.delete("/{task_id}")
async def delete_transcription(task_id: int, db=Depends(get_db)):
    await db.delete_task(task_id)
    return {"message": "Task deleted"}
