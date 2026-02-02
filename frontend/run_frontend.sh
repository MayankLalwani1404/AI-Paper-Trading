#!/bin/bash

echo ""
echo "=========================================="
echo "AI Paper Trading - Frontend Setup & Run"
echo "=========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Navigate to frontend directory
cd "$(dirname "$0")" || exit

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
fi

echo ""
echo "Starting frontend development server..."
echo ""
echo "Frontend will be available at: http://localhost:3000"
echo "Backend API at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
