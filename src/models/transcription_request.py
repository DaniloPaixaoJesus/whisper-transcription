from pydantic import BaseModel

class TranscriptionRequest(BaseModel):
    video_filename: str
    language: str
