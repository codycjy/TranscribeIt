# api/routes/models.py
from fastapi import APIRouter, HTTPException
from config import WHISPER_MODEL, AVAILABLE_PROVIDERS, MODEL_MAP
from api.schemas import ModelRequest, ModelResponse


router = APIRouter(
    prefix="/model",
    tags=["model"]
)


@router.get("/transcribe")
async def get_models():
    return {"model": WHISPER_MODEL}


@router.get("/available_providers")
async def summarize_text():
    return {"provider": AVAILABLE_PROVIDERS}


@router.post("/available_models")
async def available_models(request: ModelRequest):
    if request.provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")
    return ModelResponse(available_models=MODEL_MAP[request.provider])
