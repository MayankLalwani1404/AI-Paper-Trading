#!/bin/bash

echo ""
echo "=========================================="
echo "AI Paper Trading - Complete Deployment Test"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Test counters
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=$3
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "$expected_code" ]; then
        echo -e "${GREEN}✅ $name (HTTP $HTTP_CODE)${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ $name (HTTP $HTTP_CODE, expected $expected_code)${NC}"
        FAILED=$((FAILED + 1))
    fi
}

echo "${YELLOW}========== INFRASTRUCTURE CHECKS ==========${NC}"
echo ""

# 1. Check Docker
echo "1. Docker & PostgreSQL..."
if docker ps --format '{{.Names}}' | grep -q "papertrading-postgres"; then
    echo -e "${GREEN}✅ PostgreSQL container running${NC}"
    PASSED=$((PASSED + 1))
    
    # Test connection
    if docker exec papertrading-postgres psql -U papertrader -d papertrading -c "SELECT 1;" &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL connection successful${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ PostgreSQL connection failed${NC}"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}❌ PostgreSQL container not running${NC}"
    echo "   Start it with: docker start papertrading-postgres"
    FAILED=$((FAILED + 2))
fi

echo ""

# 2. Check Redis
echo "2. Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &>/dev/null; then
        echo -e "${GREEN}✅ Redis is running${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ Redis is not responding${NC}"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠️  redis-cli not found (continuing anyway)${NC}"
fi

echo ""
echo "${YELLOW}========== BACKEND API TESTS ==========${NC}"
echo ""

# 3. Backend Health
echo "3. Backend Health..."
test_endpoint "Health check" "http://localhost:8000/health" "200"
test_endpoint "Root endpoint" "http://localhost:8000/" "200"

echo ""
echo "4. Market Data Endpoints..."
test_endpoint "Get symbols" "http://localhost:8000/market-data/symbols?market=US" "200"
test_endpoint "Get latest price" "http://localhost:8000/market-data/latest-price?symbol=AAPL" "200"
test_endpoint "Search symbols" "http://localhost:8000/market-data/search?q=AAP" "200"

echo ""
echo "5. Indicators Endpoints..."
test_endpoint "Available indicators" "http://localhost:8000/indicators/available" "200"
test_endpoint "Get signals" "http://localhost:8000/indicators/signals?symbol=AAPL" "200"
test_endpoint "Get all indicators" "http://localhost:8000/indicators/all?symbol=AAPL" "200"

echo ""
echo "6. Trading Endpoints..."
test_endpoint "Get portfolio" "http://localhost:8000/trading/portfolio" "200"
test_endpoint "Get positions" "http://localhost:8000/trading/positions" "200"

echo ""
echo "${YELLOW}========== DATA VALIDATION TESTS ==========${NC}"
echo ""

# 7. Data Format Tests
echo "7. Response Format Validation..."

# Test symbols response format
SYMBOLS_RESPONSE=$(curl -s "http://localhost:8000/market-data/symbols?market=US")
if echo "$SYMBOLS_RESPONSE" | jq -e '.symbols | length > 0' &>/dev/null; then
    echo -e "${GREEN}✅ Symbols response valid${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Symbols response invalid${NC}"
    FAILED=$((FAILED + 1))
fi

# Test price response format
PRICE_RESPONSE=$(curl -s "http://localhost:8000/market-data/latest-price?symbol=AAPL")
if echo "$PRICE_RESPONSE" | jq -e '.price | numbers' &>/dev/null; then
    echo -e "${GREEN}✅ Price response valid (format: numeric)${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Price response invalid${NC}"
    FAILED=$((FAILED + 1))
fi

# Test signals response format
SIGNALS_RESPONSE=$(curl -s "http://localhost:8000/indicators/signals?symbol=AAPL")
if echo "$SIGNALS_RESPONSE" | jq -e '.score | numbers' &>/dev/null; then
    echo -e "${GREEN}✅ Signals response valid (score numeric)${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Signals response invalid${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "${YELLOW}========== FRONTEND TESTS ==========${NC}"
echo ""

# 8. Frontend Check
echo "8. Frontend Connectivity..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000" 2>/dev/null)
if [ "$FRONTEND_RESPONSE" = "200" ] || [ "$FRONTEND_RESPONSE" = "307" ]; then
    echo -e "${GREEN}✅ Frontend is running (HTTP $FRONTEND_RESPONSE)${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Frontend not responding (HTTP $FRONTEND_RESPONSE)${NC}"
    echo "   Start frontend with: cd frontend && bash run_frontend.sh"
fi

echo ""
echo "${YELLOW}========== PERFORMANCE CHECKS ==========${NC}"
echo ""

# 9. Response Time
echo "9. API Response Times..."

# Time market data endpoint
START=$(date +%s%N)
curl -s "http://localhost:8000/market-data/latest-price?symbol=AAPL" > /dev/null
END=$(date +%s%N)
TIME_MS=$(( (END - START) / 1000000 ))

if [ $TIME_MS -lt 1000 ]; then
    echo -e "${GREEN}✅ Market data API: ${TIME_MS}ms (Good)${NC}"
    PASSED=$((PASSED + 1))
elif [ $TIME_MS -lt 3000 ]; then
    echo -e "${YELLOW}⚠️  Market data API: ${TIME_MS}ms (Acceptable)${NC}"
else
    echo -e "${RED}❌ Market data API: ${TIME_MS}ms (Slow)${NC}"
    FAILED=$((FAILED + 1))
fi

# Time indicators endpoint
START=$(date +%s%N)
curl -s "http://localhost:8000/indicators/signals?symbol=AAPL" > /dev/null
END=$(date +%s%N)
TIME_MS=$(( (END - START) / 1000000 ))

if [ $TIME_MS -lt 1000 ]; then
    echo -e "${GREEN}✅ Indicators API: ${TIME_MS}ms (Good)${NC}"
    PASSED=$((PASSED + 1))
elif [ $TIME_MS -lt 3000 ]; then
    echo -e "${YELLOW}⚠️  Indicators API: ${TIME_MS}ms (Acceptable)${NC}"
else
    echo -e "${RED}❌ Indicators API: ${TIME_MS}ms (Slow)${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "${YELLOW}========== CACHE TESTS ==========${NC}"
echo ""

# 10. Cache Test
echo "10. Redis Cache Verification..."

# First request (cache miss)
START=$(date +%s%N)
curl -s "http://localhost:8000/market-data/latest-price?symbol=AAPL" > /dev/null
END=$(date +%s%N)
TIME_FIRST=$(( (END - START) / 1000000 ))

# Second request (cache hit)
START=$(date +%s%N)
curl -s "http://localhost:8000/market-data/latest-price?symbol=AAPL" > /dev/null
END=$(date +%s%N)
TIME_SECOND=$(( (END - START) / 1000000 ))

if [ $TIME_SECOND -lt $TIME_FIRST ]; then
    echo -e "${GREEN}✅ Cache working (First: ${TIME_FIRST}ms, Cached: ${TIME_SECOND}ms)${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Cache behavior unclear${NC}"
fi

echo ""
echo "${YELLOW}========== TEST SUMMARY ==========${NC}"
echo ""

TOTAL=$((PASSED + FAILED))
PERCENTAGE=$((PASSED * 100 / TOTAL))

echo "Tests Passed: ${GREEN}$PASSED${NC}/$TOTAL"
echo "Tests Failed: ${RED}$FAILED${NC}/$TOTAL"
echo "Success Rate: $PERCENTAGE%"

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Your AI Paper Trading platform is ready!"
    echo ""
    echo "Access:"
    echo "  Frontend:  ${BLUE}http://localhost:3000${NC}"
    echo "  Backend:   ${BLUE}http://localhost:8000${NC}"
    echo "  API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please:"
    echo "1. Verify backend is running: cd backend && bash run_backend.sh"
    echo "2. Verify PostgreSQL container: docker ps | grep postgres"
    echo "3. Check logs for errors"
    echo "4. Run test again: bash test_all.sh"
    echo ""
    exit 1
fi
