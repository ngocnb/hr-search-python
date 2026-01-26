# HR Employee Search Microservice container
FROM python:3.12-slim

# Install SQLite CLI (Python already includes libsqlite3 with FTS5 support)
RUN apt-get update \
    && apt-get install -y --no-install-recommends sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source
COPY . /app

# Disable bytecode, ensure unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Default command: run API server
CMD ["python3", "main.py", "--host=0.0.0.0", "--port=8000"]
