# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container.
COPY requirements.txt .

# Install the dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container.
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose the port that the application will run on.
EXPOSE 8080

# Set environment variables for Cloud Run
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Set the command to run the application.
CMD ["python", "simple_server.py"]
