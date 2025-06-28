# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run init_db.py before app startup (optional, or handle via CMD/entrypoint)
# CMD ["python", "init_db.py"]

# Expose port for Render
EXPOSE 8000

# Run the app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
