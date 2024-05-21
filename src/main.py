from fastapi import FastAPI
from src.controllers.transcription_controller import router as transcription_router

app = FastAPI()

app.include_router(transcription_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
