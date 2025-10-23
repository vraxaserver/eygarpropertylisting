# === Buildable, small, secure Dockerfile for FastAPI ===
FROM python:3.12-slim AS base

# Environment: avoid writing .pyc, enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/home/app/.local/bin:$PATH"

# Arguments (override at build/run time if desired)
ARG APP_USER=app
ARG APP_UID=1000
ARG PORT=8000
ENV PORT=${PORT}

WORKDIR /app

# Install system deps required to build some Python packages and to run
# (add libpq-dev or other dev libs if you need DB drivers built from source)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libpq-dev \
      curl \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first to leverage Docker cache
# Use requirements.txt (if you use poetry/poetry.lock or pyproject.toml, modify accordingly)
COPY requirements.txt .

# Upgrade pip and install dependencies into user local to avoid root site-packages issues
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create unprivileged user and chown app directory
RUN useradd -u ${APP_UID} -m ${APP_USER} \
 && chown -R ${APP_USER}:${APP_USER} /app

USER ${APP_USER}

EXPOSE ${PORT}

# Healthcheck (optional) — checks root; adjust path to /health or /ready if your app provides one
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import sys,urllib.request as u; \
try: u.urlopen(f'http://127.0.0.1:{int(${PORT})}/', timeout=2); \
except Exception as e: sys.exit(1)" || exit 1

# Default command: run Uvicorn. Replace app.main:app with your ASGI app path.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--proxy-headers", "--loop", "auto", "--http", "auto"]
