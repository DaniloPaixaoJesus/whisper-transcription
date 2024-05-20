from pydantic import BaseModel

class TranscriptionResponse(BaseModel):
    task_id: str
