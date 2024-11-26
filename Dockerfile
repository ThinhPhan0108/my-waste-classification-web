
# Use Python 3.8.20 slim base image
FROM python:3.8.20-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-distutils \
    libc-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libopenblas-dev \
    liblapack-dev \
    git \
    && apt-get clean

# Copy the project files
COPY . /app

# Upgrade pip to avoid compatibility issues
RUN pip install --upgrade pip

# Install Python dependencies from the updated requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 80 for external connections
EXPOSE 80

# Run the Flask application
CMD ["python", "app.py"]
