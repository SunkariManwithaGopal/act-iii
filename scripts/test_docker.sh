#!/usr/bin/env bash
set -e

echo "Building Docker image 'restock-backend'..."
docker build -t restock-backend .

echo "Starting container on port 8000..."
CONTAINER_ID=$(docker run -d -p 8000:8000 restock-backend)

cleanup() {
    echo "Stopping and removing container $CONTAINER_ID..."
    docker stop "$CONTAINER_ID" >/dev/null 2>&1 || true
    docker rm "$CONTAINER_ID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Sleeping 3 seconds..."
sleep 3

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/actions)
echo "HTTP response status: $STATUS"

if [ "$STATUS" -eq 200 ]; then
    echo "Test passed: Endpoint /api/actions returned 200 OK."
    exit 0
else
    echo "Test failed: Expected 200, got $STATUS"
    exit 1
fi
