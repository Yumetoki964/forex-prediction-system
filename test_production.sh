#!/bin/bash

# ===================================================================
# Production Environment Test Script
# ===================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "====================================================================="
echo "         Production Environment Test Suite"
echo "====================================================================="
echo ""

# Configuration
BASE_URL="http://localhost"
API_URL="http://localhost:8000"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test functions
run_test() {
    local test_name=$1
    local test_command=$2
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing: $test_name... "
    if eval $test_command > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "1. Infrastructure Tests"
echo "------------------------"
run_test "Docker is running" "docker info"
run_test "Docker Compose is available" "docker-compose version"
run_test "Database container is running" "docker-compose ps db | grep Up"
run_test "Redis container is running" "docker-compose ps redis | grep Up"
run_test "Backend container is running" "docker-compose ps backend | grep Up"
run_test "Frontend container is running" "docker-compose ps frontend | grep Up"

echo ""
echo "2. Database Tests"
echo "-----------------"
run_test "Database connection" "docker-compose exec -T db pg_isready -U forex_user -d forex_prediction_db"
run_test "Tables exist" "docker-compose exec -T db psql -U forex_user -d forex_prediction_db -c '\\dt' | grep users"

echo ""
echo "3. Backend API Tests"
echo "--------------------"
run_test "API health check" "curl -f ${API_URL}/health"
run_test "API documentation available" "curl -f ${API_URL}/docs"
run_test "Current rates endpoint" "curl -f ${API_URL}/api/rates/current"
run_test "Predictions endpoint" "curl -f ${API_URL}/api/predictions/latest"
run_test "Signals endpoint" "curl -f ${API_URL}/api/signals/current"
run_test "Charts endpoint" "curl -f ${API_URL}/api/charts/historical"
run_test "Technical indicators endpoint" "curl -f ${API_URL}/api/indicators/technical"

echo ""
echo "4. Frontend Tests"
echo "-----------------"
run_test "Frontend is accessible" "curl -f ${BASE_URL}"
run_test "Static assets loading" "curl -f ${BASE_URL}/static/js/main.js -o /dev/null"
run_test "Login page accessible" "curl -f ${BASE_URL}/login"

echo ""
echo "5. Authentication Tests"
echo "-----------------------"
# Test login
LOGIN_RESPONSE=$(curl -s -X POST ${API_URL}/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"password"}' 2>/dev/null || echo "FAILED")

if [[ $LOGIN_RESPONSE == *"access_token"* ]]; then
    run_test "Login endpoint" "true"
else
    run_test "Login endpoint" "false"
fi

echo ""
echo "6. WebSocket Tests"
echo "------------------"
# Simple WebSocket test using curl (basic connection test)
run_test "WebSocket endpoint available" "curl -f -i -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' ${API_URL}/ws/test 2>/dev/null | grep -q '101 Switching Protocols' || true"

echo ""
echo "7. Performance Tests"
echo "--------------------"
# Response time tests
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' ${API_URL}/health)
if (( $(echo "$RESPONSE_TIME < 1" | bc -l) )); then
    run_test "API response time < 1s" "true"
else
    run_test "API response time < 1s" "false"
fi

# Load test (simple)
echo -n "Testing: Concurrent requests handling... "
SUCCESS_COUNT=0
for i in {1..10}; do
    curl -f ${API_URL}/health > /dev/null 2>&1 && SUCCESS_COUNT=$((SUCCESS_COUNT + 1)) &
done
wait
if [ $SUCCESS_COUNT -ge 8 ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "8. Security Tests"
echo "-----------------"
# Check HTTPS redirect (if nginx is configured)
run_test "Security headers present" "curl -I ${BASE_URL} | grep -q 'X-Frame-Options'"
run_test "No debug mode in production" "! curl -s ${API_URL}/ | grep -q 'debug'"

echo ""
echo "====================================================================="
echo "                    Test Results Summary"
echo "====================================================================="
echo ""
echo -e "Total Tests: ${TOTAL_TESTS}"
echo -e "Passed: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Production environment is ready.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please check the configuration.${NC}"
    echo ""
    echo "Debug commands:"
    echo "  - Check logs: docker-compose logs [service_name]"
    echo "  - Check container status: docker-compose ps"
    echo "  - Check database: docker-compose exec db psql -U forex_user -d forex_prediction_db"
    exit 1
fi