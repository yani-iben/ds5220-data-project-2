# Use a Python base that includes necessary math libraries
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies for Matplotlib
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container
COPY app.py .

# Run the script
CMD ["python", "app.py"]