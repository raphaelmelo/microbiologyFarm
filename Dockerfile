# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . /app

# Make the run script executable
RUN chmod +x /app/run.sh

# Command to run the application.
# Cloud Run will set the PORT environment variable.
# We use 8080 as a default for local testing.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
