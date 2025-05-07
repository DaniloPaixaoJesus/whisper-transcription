FROM python:3.12

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U openai-whisper==20231117
RUN apt-get update && apt-get install -y ffmpeg

COPY . .

CMD ["uvicorn", "src.main_uvicorn:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
