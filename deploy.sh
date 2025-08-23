#!/bin/bash

# Forex Prediction System - 統合デプロイスクリプト
# Usage: ./deploy.sh [local|staging|production] [up|down|restart]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-local}
ACTION=${2:-up}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(local|staging|production)$ ]]; then
    echo -e "${RED}Error: Environment must be 'local', 'staging', or 'production'${NC}"
    exit 1
fi

# Validate action
if [[ ! "$ACTION" =~ ^(up|down|restart|logs|ps)$ ]]; then
    echo -e "${RED}Error: Action must be 'up', 'down', 'restart', 'logs', or 'ps'${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Forex Prediction System Deployment${NC}"
echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}Action: $ACTION${NC}"
echo ""

# Set environment variables
export NODE_ENV=$ENVIRONMENT

# Check if environment file exists
if [[ ! -f ".env.$ENVIRONMENT" ]]; then
    echo -e "${RED}Error: Environment file .env.$ENVIRONMENT not found${NC}"
    exit 1
fi

# Compose file configuration
COMPOSE_FILES="-f docker-compose.yml"
case $ENVIRONMENT in
    local)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.development.yml"
        ;;
    staging)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.staging.yml"
        ;;
    production)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.production.yml"
        ;;
esac

# Execute docker-compose command
case $ACTION in
    up)
        echo -e "${GREEN}Starting $ENVIRONMENT environment...${NC}"
        docker-compose $COMPOSE_FILES --env-file .env.$ENVIRONMENT up -d
        echo -e "${GREEN}✅ Services started successfully${NC}"
        echo ""
        echo -e "${BLUE}Service URLs:${NC}"
        if [[ "$ENVIRONMENT" == "local" ]]; then
            echo "  Frontend: http://localhost:3173"
            echo "  Backend:  http://localhost:8173"
            echo "  Docs:     http://localhost:8173/docs"
        fi
        ;;
    down)
        echo -e "${YELLOW}Stopping $ENVIRONMENT environment...${NC}"
        docker-compose $COMPOSE_FILES down
        echo -e "${GREEN}✅ Services stopped${NC}"
        ;;
    restart)
        echo -e "${YELLOW}Restarting $ENVIRONMENT environment...${NC}"
        docker-compose $COMPOSE_FILES --env-file .env.$ENVIRONMENT restart
        echo -e "${GREEN}✅ Services restarted${NC}"
        ;;
    logs)
        echo -e "${BLUE}Showing logs for $ENVIRONMENT environment...${NC}"
        docker-compose $COMPOSE_FILES logs -f
        ;;
    ps)
        echo -e "${BLUE}Services status for $ENVIRONMENT environment:${NC}"
        docker-compose $COMPOSE_FILES ps
        ;;
esac

# Health check for 'up' action
if [[ "$ACTION" == "up" ]]; then
    echo ""
    echo -e "${BLUE}Performing health checks...${NC}"
    
    # Wait for services to start
    sleep 5
    
    # Check backend health
    if [[ "$ENVIRONMENT" == "local" ]]; then
        BACKEND_URL="http://localhost:8173"
    else
        BACKEND_URL="http://localhost:8080"
    fi
    
    if curl -s "$BACKEND_URL/docs" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${RED}❌ Backend health check failed${NC}"
    fi
    
    # Check frontend health
    if [[ "$ENVIRONMENT" == "local" ]]; then
        FRONTEND_URL="http://localhost:3173"
    else
        FRONTEND_URL="http://localhost:80"
    fi
    
    if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${RED}❌ Frontend health check failed${NC}"
    fi
fi