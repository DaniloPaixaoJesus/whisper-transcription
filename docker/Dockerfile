# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -U openai-whisper==20231117

# Copy the entire project to the container
COPY . .

# Create necessary directories
RUN mkdir -p app/results app/tmp

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Execute o aplicativo
CMD ["py", "-m", "src.main_sqs_consumer"]