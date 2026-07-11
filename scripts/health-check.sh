#!/bin/bash
# Health check script - verify all services are running
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_pass() { echo -e "  ${GREEN}✅ $1${NC}"; }
check_fail() { echo -e "  ${RED}❌ $1${NC}"; FAILURES=$((FAILURES + 1)); }
check_warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }

FAILURES=0

echo "🏥 PM Internship Engine - Health Check"
echo "======================================"
echo ""

# Backend API
echo "🔧 Backend API (FastAPI)"
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    check_pass "Backend API is responding"
else
    check_fail "Backend API is not responding on port 8000"
fi

# Frontend
echo "🎨 Frontend (Next.js)"
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    check_pass "Frontend is responding"
else
    check_fail "Frontend is not responding on port 3000"
fi

# PostgreSQL
echo "🐘 PostgreSQL"
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        check_pass "PostgreSQL is accepting connections"
    else
        check_fail "PostgreSQL is not accepting connections"
    fi
elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q postgres; then
    check_pass "PostgreSQL container is running"
else
    check_warn "Cannot verify PostgreSQL (pg_isready not found, no docker container)"
fi

# Redis
echo "🔴 Redis"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping 2>/dev/null | grep -q PONG; then
        check_pass "Redis is responding to PING"
    else
        check_fail "Redis is not responding"
    fi
elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q redis; then
    check_pass "Redis container is running"
else
    check_warn "Cannot verify Redis (redis-cli not found, no docker container)"
fi

# OpenSearch
echo "🔍 OpenSearch"
if curl -sf http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    CLUSTER_STATUS=$(curl -sf http://localhost:9200/_cluster/health | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "unknown")
    if [ "$CLUSTER_STATUS" = "green" ] || [ "$CLUSTER_STATUS" = "yellow" ]; then
        check_pass "OpenSearch cluster is $CLUSTER_STATUS"
    else
        check_warn "OpenSearch cluster status: $CLUSTER_STATUS"
    fi
else
    check_fail "OpenSearch is not responding on port 9200"
fi

# Docker containers
echo "🐳 Docker Containers"
if command -v docker &> /dev/null; then
    RUNNING=$(docker ps --format '{{.Names}}' 2>/dev/null | wc -l)
    if [ "$RUNNING" -gt 0 ]; then
        check_pass "$RUNNING container(s) running"
        docker ps --format '     {{.Names}} - {{.Status}}' 2>/dev/null
    else
        check_warn "No Docker containers running"
    fi
else
    check_warn "Docker not installed"
fi

echo ""
echo "======================================"
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILURES check(s) failed${NC}"
    exit 1
fi
