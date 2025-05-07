from fastapi import FastAPI
from src.controllers.transcription_controller import router as transcription_router

app = FastAPI()
app.include_router(transcription_router)

# Executar com: uvicorn src.main_uvicorn:app --reload
