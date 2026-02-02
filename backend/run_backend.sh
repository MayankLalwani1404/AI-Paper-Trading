#!/bin/bash

echo ""
echo "=========================================="
echo "AI Paper Trading - Backend Server"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Activate venv
echo "Activating Python virtual environment..."
source "$PROJECT_DIR/backend/.venv/bin/activate"

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Set Python path
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Start backend
echo "Starting FastAPI server on http://0.0.0.0:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$PROJECT_DIR" || exit
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
