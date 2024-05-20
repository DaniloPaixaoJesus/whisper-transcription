# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . .

# Create necessary directories
RUN mkdir -p app/files app/tmp

# Set environment variables (replace with your actual values or pass them through the Docker run command)
ENV API_KEY="your_openai_api_key"
ENV FROM_EMAIL="your_email@example.com"
ENV FROM_PASSWORD="your_password"
ENV SMTP_SERVER="smtp.gmail.com"
ENV SMTP_PORT=587

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
