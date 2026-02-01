#!/bin/bash

# Setup script for AI Paper Trading Platform on Garuda Linux (Arch-based)
# Run this in your external terminal

set -e

PROJECT_DIR="/home/mayank/Desktop/AI Paper Trading"
cd "$PROJECT_DIR"

echo "=========================================="
echo "AI Paper Trading - Garuda Linux Setup"
echo "=========================================="
echo ""

# Step 1: Check system dependencies
echo "Step 1: Checking system dependencies..."
echo ""

check_package() {
    if pacman -Qi $1 &> /dev/null; then
        echo "✅ $1 is installed"
    else
        echo "❌ $1 is NOT installed"
        echo "   Install with: sudo pacman -S $1"
        MISSING_PACKAGES+=($1)
    fi
}

MISSING_PACKAGES=()

check_package "python"
check_package "postgresql"
check_package "redis"
check_package "python-pip"
check_package "python-virtualenv"

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo "Missing packages detected. Install them with:"
    echo "sudo pacman -S ${MISSING_PACKAGES[@]}"
    echo ""
    read -p "Do you want to install them now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo pacman -S ${MISSING_PACKAGES[@]}
    else
        echo "Please install missing packages and run this script again."
        exit 1
    fi
fi

echo ""
echo "Step 2: Setting up Python virtual environment..."
echo ""

# Remove old venv if exists
if [ -d "backend/.venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf backend/.venv
fi

# Create new venv with system python
python -m venv backend/.venv

echo "✅ Virtual environment created"

# Activate venv
source backend/.venv/bin/activate

echo "✅ Virtual environment activated"
echo "   Python: $(which python)"
echo "   Version: $(python --version)"

echo ""
echo "Step 3: Upgrading pip..."
echo ""

python -m pip install --upgrade pip setuptools wheel

echo ""
echo "Step 4: Installing Python dependencies..."
echo ""

# Install packages one by one to catch errors
pip install fastapi uvicorn[standard] pydantic pydantic-settings
pip install sqlalchemy psycopg2-binary
pip install redis
pip install yfinance pandas numpy
pip install python-dotenv requests python-multipart

echo ""
echo "✅ All Python packages installed successfully!"

echo ""
echo "Step 5: Verifying PostgreSQL (Docker)..."
echo ""

# Check if Docker PostgreSQL container is running
if docker ps --format '{{.Names}}' | grep -q "papertrading-postgres"; then
    echo "✅ Docker PostgreSQL container is running"
    
    # Verify database and user exist
    if docker exec papertrading-postgres psql -U papertrader -d papertrading -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ Database 'papertrading' and user 'papertrader' verified"
    else
        echo "❌ Database verification failed"
        exit 1
    fi
else
    echo "❌ Docker PostgreSQL container 'papertrading-postgres' is not running"
    echo "Please start it with: docker start papertrading-postgres"
    exit 1
fi

echo "✅ PostgreSQL setup complete"

echo ""
echo "Step 6: Setting up Redis..."
echo ""

# Check if Redis is running
if systemctl is-active --quiet redis; then
    echo "✅ Redis is running"
else
    echo "Starting Redis..."
    sudo systemctl start redis
    sudo systemctl enable redis
    echo "✅ Redis started and enabled"
fi

# Test Redis
redis-cli ping > /dev/null && echo "✅ Redis connection successful"

echo ""
echo "Step 7: Initializing database tables..."
echo ""

# Set PYTHONPATH and run from project root
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
cd "$PROJECT_DIR"
python -m backend.create_tables

echo "✅ Database tables created"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To run the backend:"
echo "  1. cd '$PROJECT_DIR'"
echo "  2. source backend/.venv/bin/activate"
echo "  3. uvicorn backend.main:app --reload"
echo ""
echo "Or run: bash run_backend.sh"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
