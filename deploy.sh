#!/bin/bash

# ===================================================================
# Forex Prediction System - Production Deployment Script
# ===================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="forex-prediction-system"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.production"

# Functions
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Header
echo "====================================================================="
echo "           Forex Prediction System - Production Deployment          "
echo "====================================================================="
echo ""

# 1. Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_status "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_status "Docker Compose is installed"

# Check environment file
if [ ! -f "backend/$ENV_FILE" ]; then
    print_warning "Production environment file not found. Creating from template..."
    cp backend/.env.production backend/.env.production
    print_warning "Please update backend/.env.production with your production values"
    exit 1
fi
print_status "Environment file found"

# 2. Build Docker images
echo ""
print_status "Building Docker images..."
docker-compose build --no-cache

# 3. Pull latest images
echo ""
print_status "Pulling latest base images..."
docker-compose pull

# 4. Stop existing containers
echo ""
print_status "Stopping existing containers..."
docker-compose down

# 5. Start database and redis first
echo ""
print_status "Starting database and cache services..."
docker-compose up -d db redis

# Wait for database to be ready
echo ""
print_status "Waiting for database to be ready..."
sleep 10

# Check database health
MAX_TRIES=30
TRIES=0
while [ $TRIES -lt $MAX_TRIES ]; do
    if docker-compose exec -T db pg_isready -U forex_user -d forex_prediction_db > /dev/null 2>&1; then
        print_status "Database is ready"
        break
    fi
    TRIES=$((TRIES + 1))
    echo -n "."
    sleep 2
done

if [ $TRIES -eq $MAX_TRIES ]; then
    print_error "Database failed to start"
    exit 1
fi

# 6. Run database migrations
echo ""
print_status "Running database migrations..."
docker-compose run --rm backend alembic upgrade head

# 7. Start all services
echo ""
print_status "Starting all services..."
docker-compose up -d

# 8. Wait for services to be healthy
echo ""
print_status "Waiting for services to be healthy..."
sleep 15

# 9. Health checks
echo ""
print_status "Running health checks..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend API is healthy"
else
    print_error "Backend API health check failed"
    exit 1
fi

# Check frontend
if curl -f http://localhost:80 > /dev/null 2>&1; then
    print_status "Frontend is accessible"
else
    print_error "Frontend health check failed"
    exit 1
fi

# 10. Show running containers
echo ""
print_status "Running containers:"
docker-compose ps

# 11. Clean up
echo ""
print_status "Cleaning up unused resources..."
docker system prune -f

# Success message
echo ""
echo "====================================================================="
echo -e "${GREEN}       Deployment completed successfully!${NC}"
echo "====================================================================="
echo ""
echo "Access points:"
echo "  - Frontend:    http://localhost"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - pgAdmin:     http://localhost:5050 (if enabled)"
echo "  - Prometheus:  http://localhost:9090 (if enabled)"
echo "  - Grafana:     http://localhost:3000 (if enabled)"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service_name]"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""