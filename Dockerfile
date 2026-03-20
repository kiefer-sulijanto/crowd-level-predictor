FROM python:3.13-slim

# 1. Install system tools (Seldom changes)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Copy ONLY requirements first (The "Secret Sauce")
COPY requirements.txt .

# 3. Install Python libs (Only reruns if requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the code (Changes often, but it's fast)
COPY . .

# 5. Create a non-root user (Security Best Practice)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Use a default CMD that can be easily overridden
CMD ["python", "-c", "print('No default entry point defined. Use docker-compose to specify commands.')"]