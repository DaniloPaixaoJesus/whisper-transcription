# Transcription App

This application is a transcription service built using FastAPI. It provides endpoints to transcribe videos either by uploading a file or by providing a URL to the video. The application processes the transcription and sends the results via email.

## Features

- Transcribe audio from video files.
- Summarize transcriptions using OpenAI's GPT-4.
- Upload video files or provide URLs to download and transcribe.
- Send transcription and summary via email.

## Project Structure


## Installation

### Prerequisites

- Python 3.9+
- Docker (optional, for containerization)

### Steps

1. Clone the repository:

```sh
git clone https://github.com/yourusername/transcription_app.git
cd transcription_app


pip install -r requirements.txt

export API_KEY="your_openai_api_key"
export FROM_EMAIL="your_email@example.com"
export FROM_PASSWORD="your_email_password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT=587


uvicorn app.main:app --reload

docker build -t transcription-app -f docker/Dockerfile .

docker run -d -p 8000:8000 --name transcription-app \
  -e API_KEY=your_openai_api_key \
  -e FROM_EMAIL=your_email@example.com \
  -e FROM_PASSWORD=your_email_password \
  transcription-app

docker-compose up --build


transcription_app/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── files/             # Output files directory
│   ├── tmp/               # Temporary files directory
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── transcription_controller.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── transcription_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transcription_request.py
│   │   └── transcription_response.py
│   └── utils/
│       ├── __init__.py
│       ├── email_utils.py
│       ├── download_utils.py
│       ├── s3_utils.py
│       └── mongodb_utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_transcription_service.py
│   └── test_transcription_controller.py
│
├── docker/
│   └── Dockerfile
│
├── docker-compose.yml     # Docker Compose configuration file
├── requirements.txt
└── README.md
