#!/bin/bash
# Just run this script to start the challenge!
# Usage: ./START.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "         Companion CTF Challenge          "
echo "=========================================="
echo ""

# Load Docker image if not already loaded
if ! docker image inspect mwc-companion:release &>/dev/null; then
    if [ -f "mwc-companion-image.tar" ]; then
        echo "Loading Docker image..."
        docker load < mwc-companion-image.tar
        echo "OK: Image loaded"
        echo ""
    else
        echo "ERROR: Docker image not found!"
        echo "  Expected file: mwc-companion-image.tar"
        exit 1
    fi
else
    echo "OK: Docker image already loaded"
fi

# Start the challenge
echo "Starting challenge..."
docker compose up -d

echo ""
echo "=========================================="
echo "  Challenge is running!"
echo "=========================================="
echo ""
echo "  URL: http://127.0.0.1:8080"
echo ""
echo "  Commands:"
echo "    Stop:    docker compose down"
echo "    Restart: ./START.sh"
echo "    Logs:    docker compose logs -f"
echo ""
