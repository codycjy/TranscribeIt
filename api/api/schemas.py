from pydantic import BaseModel, HttpUrl
from typing import Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    SUMMARY_FAILED = "summary_failed"
    FAILED = "failed"


class TranscriptionRequest(BaseModel):
    url: HttpUrl


class SummaryRequest(BaseModel):
    provider: str = "openai"
    model: Optional[str] = None
    max_length: Optional[int] = None


class TranscriptionResponse(BaseModel):
    id: int
    youtube_url: str
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: TaskStatus
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class ModelRequest(BaseModel):
    provider: str

class ModelResponse(BaseModel):
    available_models: list[str]
