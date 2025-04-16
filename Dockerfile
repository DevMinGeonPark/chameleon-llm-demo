FROM python:3.8.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional requirements for web app
RUN pip install fastapi uvicorn streamlit

# Create data directories
RUN mkdir -p /app/data/scienceqa /app/data/tabmwp

# Copy data files
COPY data/scienceqa/* /app/data/scienceqa/
COPY data/tabmwp/* /app/data/tabmwp/

# Copy the rest of the application
COPY . .

# Create results directories
RUN mkdir -p /app/results/scienceqa /app/results/tabmwp

# Expose ports
EXPOSE 8501
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_ROOT=/app/data
ENV OUTPUT_ROOT=/app/results

# Command to run the application
CMD ["streamlit", "run", "web_app/app.py"] 