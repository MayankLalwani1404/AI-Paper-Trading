#!/bin/bash

# COMPLETE RUN SCRIPT - Everything needed to run the platform

PROJECT_DIR="/home/mayank/Desktop/AI Paper Trading"
cd "$PROJECT_DIR" || exit

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "     🚀 AI PAPER TRADING - STARTING ALL SERVICES"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "1️⃣  Starting Backend..."
echo ""

cd "$PROJECT_DIR/backend" || exit

# Activate venv
if [ ! -f ".venv/bin/activate" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install requirements if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "   Installing Python packages..."
    pip install -q -r requirements.txt
fi

# Start backend in background
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "   ✅ Backend started (PID: $BACKEND_PID)"
else
    echo "   ❌ Backend failed to start"
    cat /tmp/backend.log
    exit 1
fi

echo ""
echo "2️⃣  Starting Frontend..."
echo ""

cd "$PROJECT_DIR/frontend" || exit

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "   Installing npm packages (this may take a minute)..."
    npm install -q
fi

# Start frontend in background
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "   ❌ Frontend failed to start"
    cat /tmp/frontend.log
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "   ✅ ALL SERVICES ARE RUNNING!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📍 Access Points:"
echo "   🌐 Frontend:  http://localhost:3000"
echo "   🔌 Backend:   http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Keep running
wait
