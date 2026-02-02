#!/bin/bash

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  AI PAPER TRADING - COMPLETE SETUP & RUN GUIDE"
echo "═══════════════════════════════════════════════════════════════"
echo ""

PROJECT_DIR="/home/mayank/Desktop/AI Paper Trading"

# Function to print section
print_section() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Verify environment
print_section "STEP 1: VERIFYING ENVIRONMENT"

echo "Checking prerequisites..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    if docker ps --format '{{.Names}}' | grep -q "papertrading-postgres"; then
        echo "✅ Docker PostgreSQL container running"
    else
        echo "⚠️  Docker running but PostgreSQL container not found"
        echo "    Starting: docker start papertrading-postgres"
        docker start papertrading-postgres 2>/dev/null
    fi
else
    echo "❌ Docker not found"
    exit 1
fi

# Check Redis
if redis-cli ping &>/dev/null; then
    echo "✅ Redis running"
else
    echo "⚠️  Redis not responding"
fi

echo ""

# Setup Backend
print_section "STEP 2: SETTING UP BACKEND"

cd "$PROJECT_DIR" || exit

echo "Making backend script executable..."
chmod +x backend/run_backend.sh

if [ ! -f "backend/.venv/bin/activate" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv backend/.venv
    
    echo "Activating venv..."
    source backend/.venv/bin/activate
    
    echo "Installing Python packages..."
    pip install --upgrade pip setuptools wheel
    pip install -r backend/requirements.txt
    echo "✅ Backend setup complete"
else
    echo "✅ Python venv already exists"
fi

echo ""

# Setup Frontend
print_section "STEP 3: SETTING UP FRONTEND"

if [ ! -d "frontend/node_modules" ]; then
    echo "Installing npm dependencies..."
    cd frontend || exit
    npm install 2>&1 | tail -20
    cd "$PROJECT_DIR" || exit
    echo "✅ Frontend dependencies installed"
else
    echo "✅ Frontend dependencies already installed"
fi

chmod +x frontend/run_frontend.sh

echo ""

# Summary
print_section "✅ SETUP COMPLETE"

echo "All services are configured and ready!"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 READY TO RUN - Choose One Option Below               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "OPTION 1: Run Everything at Once"
echo "  $ cd '$PROJECT_DIR'"
echo "  $ bash run_all.sh"
echo ""

echo "OPTION 2: Run Manually (Recommended)"
echo ""
echo "  Terminal 1 - Backend:"
echo "    $ cd '$PROJECT_DIR/backend'"
echo "    $ bash run_backend.sh"
echo ""
echo "  Terminal 2 - Frontend:"
echo "    $ cd '$PROJECT_DIR/frontend'"
echo "    $ bash run_frontend.sh"
echo ""
echo "  Terminal 3 - Testing (optional):"
echo "    $ cd '$PROJECT_DIR'"
echo "    $ bash test_all.sh"
echo ""

echo "OPTION 3: Run with Manual Commands"
echo ""
echo "  Terminal 1 - Backend:"
echo "    $ cd '$PROJECT_DIR'"
echo "    $ source backend/.venv/bin/activate"
echo "    $ export PYTHONPATH='$PROJECT_DIR:\$PYTHONPATH'"
echo "    $ python -m uvicorn backend.main:app --reload --port 8000"
echo ""
echo "  Terminal 2 - Frontend:"
echo "    $ cd '$PROJECT_DIR/frontend'"
echo "    $ npm run dev"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  📍 Access Points                                         ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Frontend:  http://localhost:3000                         ║"
echo "║  Backend:   http://localhost:8000                         ║"
echo "║  API Docs:  http://localhost:8000/docs                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "Ready to start? Run one of the options above!"
echo ""
