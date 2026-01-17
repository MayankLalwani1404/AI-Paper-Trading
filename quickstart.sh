#!/bin/bash

# Quick Start Script for AI Paper Trading Platform
# This script sets up the development environment automatically

set -e

echo "================================"
echo "AI Paper Trading - Quick Setup"
echo "================================"
echo ""

# Check for required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
    echo "✅ $1 found"
}

echo "Checking prerequisites..."
check_command python3
check_command git
check_command psql
check_command redis-cli

echo ""
echo "Setting up Python virtual environment..."
python3 -m venv backend/.venv
source backend/.venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo ""
echo "Setting up PostgreSQL..."
# Note: This assumes you have PostgreSQL running and access
# Adjust the credentials in .env if needed

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << EOF
DATABASE_URL=postgresql://papertrader:papertraderpass@localhost:5432/papertrading
REDIS_URL=redis://localhost:6379
OLLAMA_BASE_URL=http://localhost:11434
APP_NAME=Paper Trading Backend
DEBUG=true
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "Initializing database..."
python backend/create_tables.py || echo "⚠️ Could not initialize database. Ensure PostgreSQL is running."

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Ensure PostgreSQL is running:   sudo systemctl start postgresql"
echo "2. Ensure Redis is running:        redis-server"
echo "3. Start Ollama (optional):        ollama serve"
echo "4. Start the backend server:       uvicorn backend.main:app --reload"
echo "5. Open API docs:                  http://localhost:8000/docs"
echo ""
echo "For more information, see SETUP_GUIDE.md"
