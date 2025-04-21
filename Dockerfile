# Use a lightweight Python base
FROM python:3.11-slim

# Don’t write .pyc files, and flush logs immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Copy only requirements first (so Docker caches installs)
COPY requirements.txt .

# Install system deps + Python deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && pip install --upgrade pip setuptools \
 && pip install -r requirements.txt \
 && apt-get purge -y --auto-remove gcc \
 && rm -rf /var/lib/apt/lists/*

# Bring in your app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Default command
CMD ["streamlit", "run", "src/app.py", "--server.headless", "true"]
