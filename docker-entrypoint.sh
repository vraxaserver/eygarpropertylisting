#!/bin/sh
set -e

echo "Starting container..."


# Path for marker file (can be in /app, /tmp, or a persistent volume)
INIT_MARKER="/app/.initialized"


# Continue to run main CMD
echo "Starting main application..."
exec "$@"
