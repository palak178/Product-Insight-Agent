# Use an official Python base image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copy the .env file to the container
COPY .env .env

# Expose FastAPI default port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
