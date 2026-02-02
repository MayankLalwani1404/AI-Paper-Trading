#!/bin/bash

echo ""
echo "=========================================="
echo "AI Paper Trading - Full Stack Testing"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "${BLUE}Testing Backend API...${NC}"
echo ""

# Backend health check
echo "1. Health check..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not responding (HTTP $HEALTH)${NC}"
    echo "   Make sure backend is running: cd backend && bash run_backend.sh"
    exit 1
fi

echo ""
echo "2. Market data endpoints..."

# Test market data
SYMBOLS=$(curl -s http://localhost:8000/market-data/symbols?market=US | jq '.symbols[0]' 2>/dev/null)
if [ ! -z "$SYMBOLS" ] && [ "$SYMBOLS" != "null" ]; then
    echo -e "${GREEN}✅ Market data API working${NC}"
else
    echo -e "${RED}❌ Market data API failed${NC}"
fi

echo ""
echo "3. Indicators endpoints..."

# Test indicators
INDICATORS=$(curl -s http://localhost:8000/indicators/available | jq '.indicators | length' 2>/dev/null)
if [ "$INDICATORS" -gt 0 ] 2>/dev/null; then
    echo -e "${GREEN}✅ Indicators API working${NC}"
else
    echo -e "${RED}❌ Indicators API failed${NC}"
fi

echo ""
echo "4. Trading endpoints..."

# Test trading
PORTFOLIO=$(curl -s http://localhost:8000/trading/portfolio | jq '.' 2>/dev/null)
if [ ! -z "$PORTFOLIO" ]; then
    echo -e "${GREEN}✅ Trading API working${NC}"
else
    echo -e "${RED}❌ Trading API failed${NC}"
fi

echo ""
echo "${BLUE}Testing Frontend...${NC}"
echo ""

# Check if frontend is running
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$FRONTEND" = "200" ] || [ "$FRONTEND" = "307" ]; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
    echo ""
    echo "${GREEN}✅ Full Stack is Ready!${NC}"
    echo ""
    echo "Access the application:"
    echo "  Frontend: ${BLUE}http://localhost:3000${NC}"
    echo "  Backend API: ${BLUE}http://localhost:8000${NC}"
    echo "  API Docs: ${BLUE}http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Frontend is not running${NC}"
    echo "   Start frontend in another terminal: cd frontend && bash run_frontend.sh"
fi

echo ""
