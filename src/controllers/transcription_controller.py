from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid
from src.services.transcription_service import process_transcription

router = APIRouter(prefix="/transcription")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    tmp_dir = os.path.join("src", "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    # Gera nome único para evitar conflitos simultâneos
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = os.path.join(tmp_dir, unique_filename)

    # Salva o arquivo
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    # Agendamento do processamento em segundo plano
    background_tasks.add_task(process_transcription, temp_file_path, "portuguese")

    # Retorna 202 Accepted
    return JSONResponse(
        status_code=202,
        content={"message": "Arquivo recebido. A transcrição será processada em segundo plano."}
    )
