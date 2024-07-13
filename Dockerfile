# Use the official Python image from the Docker Hub
FROM python:3.12.3-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application to the working directory
COPY . .

# Command to run the application
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]