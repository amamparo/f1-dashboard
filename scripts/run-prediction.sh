#!/usr/bin/env bash
set -euo pipefail

# Run the prediction Lambda locally.
# Starts the API, runs the model, then shuts the API down.
#
# Usage:
#   ./scripts/run_prediction.sh          # predict latest race
#   ./scripts/run_prediction.sh 1100     # predict race 1100

RACE_ID="${1:-}"
API_PORT="${API_PORT:-9000}"
API_URL="http://localhost:${API_PORT}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PREDICTIONS_DIR="${PROJECT_DIR}/predictions"
VENV_DIR="${PREDICTIONS_DIR}/.venv"
API_PID=""

cleanup() {
    if [ -n "$API_PID" ]; then
        echo "==> Stopping API (pid ${API_PID})..."
        kill "$API_PID" 2>/dev/null || true
        wait "$API_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Start the API in the background
echo "==> Starting API on port ${API_PORT}..."
PORT="$API_PORT" fastapi dev "${PROJECT_DIR}/esm_fullstack_challenge/main.py" \
    --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

# Wait for the API to become ready
echo "==> Waiting for API..."
for i in $(seq 1 30); do
    if curl -sf "${API_URL}/ping" > /dev/null 2>&1; then
        echo "==> API is ready"
        break
    fi
    if ! kill -0 "$API_PID" 2>/dev/null; then
        echo "Error: API process exited unexpectedly"
        exit 1
    fi
    sleep 1
done

if ! curl -sf "${API_URL}/ping" > /dev/null 2>&1; then
    echo "Error: API failed to start within 30 seconds"
    exit 1
fi

# Create venv and install deps if needed
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "==> Installing dependencies..."
"${VENV_DIR}/bin/pip" install -q -r "${PREDICTIONS_DIR}/requirements.txt"

# Run the handler
echo "==> Running prediction model..."
if [ -n "$RACE_ID" ]; then
    API_URL="$API_URL" "${VENV_DIR}/bin/python" "${PREDICTIONS_DIR}/handler.py" "$RACE_ID"
else
    API_URL="$API_URL" "${VENV_DIR}/bin/python" "${PREDICTIONS_DIR}/handler.py"
fi

echo "==> Done"
