from fastapi import APIRouter, BackgroundTasks
from src.services.transcription_service import process_transcription
from src.models.transcription_request import TranscriptionRequest
from src.models.transcription_response import TranscriptionResponse
import uuid

router = APIRouter()

@router.post("/transcription", response_model=TranscriptionResponse, status_code=202)
async def transcription(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_transcription, request.video_filename, request.language)
    return TranscriptionResponse(task_id=task_id)

"""@router.post("/transcription_from_url", response_model=TranscriptionResponse, status_code=202)
async def transcription_from_url(url: str, language: str, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_transcription_from_url, url, language)
    return TranscriptionResponse(task_id=task_id)"""
