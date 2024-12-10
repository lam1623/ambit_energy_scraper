# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
        chromium-driver \
        chromium \
        wget \
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create app directory
RUN mkdir /app
WORKDIR /app

# Copy the script into the container
COPY ambit_energy_scraper.py /app/

# Make the script executable
RUN chmod +x /app/ambit_energy_scraper.py

# Define the default command
CMD ["/bin/bash", "/app/run.sh"]

