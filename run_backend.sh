#!/bin/bash

# Run backend server for AI Paper Trading Platform
# This script activates venv and starts the FastAPI server

PROJECT_DIR="/home/mayank/Desktop/AI Paper Trading"
cd "$PROJECT_DIR"

# Check if venv exists
if [ ! -d "backend/.venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: bash setup_garuda.sh"
    exit 1
fi

# Activate venv
source backend/.venv/bin/activate

echo "=========================================="
echo "Starting AI Paper Trading Backend"
echo "=========================================="
echo ""
echo "Python: $(which python)"
echo "Version: $(python --version)"
echo ""
echo "Starting server..."
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
