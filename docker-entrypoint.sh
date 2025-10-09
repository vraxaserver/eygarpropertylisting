#!/bin/sh
set -e

echo "Starting container..."

if [ -w /etc/resolv.conf ]; then
  echo "nameserver 8.8.8.8" > /etc/resolv.conf
else
  echo "Cannot modify /etc/resolv.conf (read-only), skipping DNS override"
fi

# Path for marker file (can be in /app, /tmp, or a persistent volume)
INIT_MARKER="/app/.initialized"

if [ ! -f "$INIT_MARKER" ]; then
    echo "Running database migrations..."
    alembic upgrade head || { echo "Alembic migration failed!"; exit 1; }

    echo "Running initialization script..."
    python scripts/initialize_data.py || { echo "Initialization failed!"; exit 1; }

    echo "Initialization completed. Creating marker file."
    touch "$INIT_MARKER"
else
    echo "Initialization already completed — skipping migrations and data setup."
fi

# Continue to run main CMD
echo "Starting main application..."
exec "$@"
