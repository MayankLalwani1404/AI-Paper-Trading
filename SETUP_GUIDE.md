# Installation & Setup Guide

## Prerequisites

- **Python**: 3.10 or higher
- **PostgreSQL**: 13 or higher (for database)
- **Redis**: 6.0 or higher (for caching)
- **Ollama**: Latest version (for local LLM support)
- **Git**: For version control

## System Requirements

- **RAM**: Minimum 8GB (recommended 16GB for AI models)
- **Disk Space**: 10GB minimum for datasets and models
- **OS**: Linux, macOS, or Windows (with WSL2 recommended)

---

## Step 1: Clone & Setup Repository

```bash
# Clone the repository
git clone <repository-url>
cd "AI Paper Trading"

# Create Python virtual environment
python3 -m venv backend/.venv

# Activate virtual environment
# On Linux/macOS:
source backend/.venv/bin/activate
# On Windows:
backend\.venv\Scripts\activate
```

---

## Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Note**: If you encounter issues with specific packages:
- For PostgreSQL: `pip install psycopg2-binary` or `brew install libpq` (macOS)
- For PyTorch: Visit https://pytorch.org for GPU-specific instructions
- For TensorFlow: May require additional setup for your hardware

---

## Step 3: Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```dotenv
# Database
DATABASE_URL=postgresql://papertrader:papertraderpass@localhost:5432/papertrading

# Redis
REDIS_URL=redis://localhost:6379

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Application
APP_NAME="Paper Trading Backend"
DEBUG=true
```

---

## Step 4: PostgreSQL Setup

### On Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE USER papertrader WITH PASSWORD 'papertraderpass';
CREATE DATABASE papertrading OWNER papertrader;
GRANT ALL PRIVILEGES ON DATABASE papertrading TO papertrader;
\c papertrading
GRANT ALL ON SCHEMA public TO papertrader;
EOF
```

### On macOS

```bash
# Install PostgreSQL (using Homebrew)
brew install postgresql

# Start PostgreSQL
brew services start postgresql

# Create database and user
createuser -P papertrader
createdb -O papertrader papertrading
```

### On Windows

1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. During installation, set the password to `papertraderpass`
3. Ensure PostgreSQL service is running

### Verify Connection

```bash
psql -U papertrader -d papertrading -h localhost
```

---

## Step 5: Redis Setup

### On Linux

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping  # Should return PONG
```

### On macOS

```bash
# Install Redis
brew install redis

# Start Redis
brew services start redis

# Verify Redis is running
redis-cli ping  # Should return PONG
```

### On Windows

1. Download WSL2 (Windows Subsystem for Linux)
2. Install Redis through WSL2 using Linux instructions
   OR
3. Use Docker: `docker run -d -p 6379:6379 redis:latest`

---

## Step 6: Initialize Database

```bash
# Activate virtual environment (if not already)
source backend/.venv/bin/activate  # Linux/macOS

# Create database tables
python backend/create_tables.py
```

Expected output:
```
✓ Database tables created successfully
✓ Connected to PostgreSQL at postgresql://localhost/papertrading
```

---

## Step 7: Setup Ollama (Optional, for AI Features)

### Installation

```bash
# Download and install Ollama
# From: https://ollama.ai

# On macOS/Linux, after installation:
ollama serve
```

### Download a Model

In a new terminal:

```bash
# Download Mistral (recommended for chat, ~4GB)
ollama pull mistral

# Or other models:
ollama pull neural-chat     # Smaller, faster (~2GB)
ollama pull llama2          # Larger, more capable (~7GB)
ollama pull orca-mini       # Compact option (~1GB)
```

### Test Ollama Connection

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "What is stock trading?",
  "stream": false
}'
```

---

## Step 8: Download & Verify Datasets

Datasets are already in the `/datasets/` folder:

```bash
# List available datasets
ls -la datasets/

# Expected files:
# - AAPL_historical.csv
# - ADANIPORTS.csv
# - BTCUSDT_5m_2017-09-01_to_2025-09-23.csv
# - historical_stock_prices.csv
# - ohlc.csv
```

All datasets should be offline-available. If any are missing, download them manually:
- AAPL data: Yahoo Finance
- Indian stocks: NSE/BSE historical data
- Crypto data: Binance/CoinGecko
- Place in `/datasets/` folder

---

## Step 9: Start the Backend Server

```bash
# Activate virtual environment
source backend/.venv/bin/activate  # Linux/macOS
# or
backend\.venv\Scripts\activate     # Windows

# Start FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Access the API

- **API Root**: http://localhost:8000
- **API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## Step 10: Verify Backend is Working

```bash
# In another terminal, test the API
curl http://localhost:8000/

# Expected response:
# {
#   "status": "ok",
#   "message": "Paper Trading Backend is running"
# }
```

### Test Market Data Endpoint

```bash
curl "http://localhost:8000/market-data/ohlcv?symbol=AAPL&interval=1d"
```

### Test Indicators Endpoint

```bash
curl -X POST "http://localhost:8000/indicators/calculate?symbol=AAPL&indicator=RSI&period=14"
```

---

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_indicators.py
```

### Code Quality Checks

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Troubleshooting

### Issue: "Connection refused" to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                 # macOS

# Check connection
psql -U papertrader -h localhost -d papertrading
```

### Issue: "Connection refused" to Redis

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
sudo systemctl start redis-server  # Linux
brew services start redis           # macOS
```

### Issue: Python packages fail to install

**Solution:**
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Try installing requirements again
pip install -r requirements.txt --no-cache-dir
```

### Issue: Ollama connection error

**Solution:**
```bash
# Start Ollama service
ollama serve

# In another terminal, verify connection
curl http://localhost:11434/api/tags
```

### Issue: "ModuleNotFoundError" when running backend

**Solution:**
```bash
# Ensure virtual environment is activated
source backend/.venv/bin/activate

# Reinstall packages
pip install -r requirements.txt

# Try running again
uvicorn backend.main:app --reload
```

---

## Production Deployment

### Before Going Live

1. **Environment Variables**
   - Change `DEBUG=false`
   - Use strong database passwords
   - Configure Redis with authentication
   - Set up SSL/TLS for API endpoints

2. **Security**
   - Enable HTTPS/SSL
   - Implement rate limiting
   - Add CORS configuration
   - Use environment-specific secrets

3. **Monitoring**
   - Setup logging
   - Monitor database performance
   - Track Redis memory usage
   - Set up alerting

4. **Scaling**
   - Use process manager (systemd, supervisor)
   - Consider load balancing
   - Implement caching strategies
   - Database query optimization

### Deployment Options

- **Docker**: Containerize backend and services
- **Cloud Platforms**: AWS, Google Cloud, Azure
- **Traditional VPS**: DigitalOcean, Linode, Heroku
- **Kubernetes**: For enterprise-scale deployments

---

## Next Steps

1. ✅ Backend setup complete
2. ⬜ Start building Next.js frontend
3. ⬜ Integrate Ollama for AI features
4. ⬜ Build backtesting engine
5. ⬜ Deploy to production

---

## Support & Documentation

- **API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Development Plan**: See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)
- **GitHub Repository**: [Link to repo]
- **Issues & Bug Reports**: Create a GitHub issue

---

## Quick Reference Commands

```bash
# Activate virtual environment
source backend/.venv/bin/activate

# Start all services (in separate terminals)
# Terminal 1: PostgreSQL
sudo systemctl start postgresql

# Terminal 2: Redis
redis-server

# Terminal 3: Ollama (optional)
ollama serve

# Terminal 4: Backend API
uvicorn backend.main:app --reload

# Test API
curl http://localhost:8000/

# Access Swagger UI
open http://localhost:8000/docs
```

