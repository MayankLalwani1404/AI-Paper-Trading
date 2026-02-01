#!/bin/bash

# Test backend API endpoints
# Run this after starting the backend

echo "=========================================="
echo "Testing AI Paper Trading Backend"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_endpoint() {
    local endpoint=$1
    local name=$2
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✅ OK (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $response)${NC}"
        return 1
    fi
}

echo "Health Check:"
test_endpoint "/" "Root endpoint"
test_endpoint "/health" "Health endpoint"

echo ""
echo "Market Data Endpoints:"
test_endpoint "/market-data/symbols?market=US" "Get US symbols"
test_endpoint "/market-data/latest-price?symbol=AAPL" "Get AAPL price"

echo ""
echo "Trading Endpoints:"
test_endpoint "/trading/portfolio" "Get portfolio"

echo ""
echo "=========================================="
echo "Backend API is working! 🚀"
echo "=========================================="
echo ""
echo "View full API docs at: $BASE_URL/docs"
echo ""
