#!/bin/bash

echo ""
echo "=========================================="
echo "AI Paper Trading - Start All Services"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait 2>/dev/null
    echo "Goodbye!"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting Backend..."
cd "$PROJECT_DIR/backend" || exit
bash run_backend.sh &
BACKEND_PID=$!
sleep 3

echo ""
echo "Starting Frontend..."
cd "$PROJECT_DIR/frontend" || exit
bash run_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ All services are running!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait
