#!/usr/bin/env bash
# ============================================================
# Setup Script - PM Internship Smart Allocation Engine
# One-command local development setup
# ============================================================

set -euo pipefail

# Colors
BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ─────────────────────────────────────────────
# Prerequisites Check
# ─────────────────────────────────────────────

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()

    command -v docker &>/dev/null || missing+=("docker")
    command -v docker compose &>/dev/null || missing+=("docker-compose")
    command -v python3 &>/dev/null || missing+=("python3")
    command -v node &>/dev/null || missing+=("node")
    command -v npm &>/dev/null || missing+=("npm")

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing[*]}"
        log_error "Please install them before running this script."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$(echo "$PYTHON_VERSION < 3.11" | bc -l)" -eq 1 ]]; then
        log_error "Python 3.11+ required (found $PYTHON_VERSION)"
        exit 1
    fi

    # Check Node version
    NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        log_error "Node.js 18+ required (found v$NODE_VERSION)"
        exit 1
    fi

    log_success "All prerequisites met"
}

# ─────────────────────────────────────────────
# Environment File
# ─────────────────────────────────────────────

setup_env() {
    log_info "Setting up environment file..."

    if [ ! -f .env ]; then
        cp .env.development .env
        log_success "Created .env from .env.development"
    else
        log_warn ".env already exists, skipping"
    fi
}

# ─────────────────────────────────────────────
# Python Virtual Environment
# ─────────────────────────────────────────────

setup_python() {
    log_info "Setting up Python virtual environment..."

    if [ ! -d "backend/.venv" ]; then
        python3 -m venv backend/.venv
        log_success "Created Python virtual environment"
    else
        log_warn "Virtual environment already exists"
    fi

    source backend/.venv/bin/activate

    log_info "Installing Python dependencies..."
    pip install --upgrade pip --quiet
    pip install -r backend/requirements.txt -r backend/requirements-dev.txt --quiet

    log_success "Python dependencies installed"
}

# ─────────────────────────────────────────────
# Node.js Dependencies
# ─────────────────────────────────────────────

setup_node() {
    log_info "Installing Node.js dependencies..."

    cd frontend
    if [ -f package-lock.json ]; then
        npm ci --silent
    else
        npm install --silent
    fi
    cd ..

    log_success "Node.js dependencies installed"
}

# ─────────────────────────────────────────────
# Docker Services
# ─────────────────────────────────────────────

start_docker() {
    log_info "Starting Docker services..."

    cd infrastructure/docker

    # Start infrastructure services first
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d \
        postgres redis opensearch temporal temporal-ui

    log_info "Waiting for services to be ready..."

    # Wait for PostgreSQL
    local retries=30
    while [ $retries -gt 0 ]; do
        if docker exec pm-postgres pg_isready -U pm_admin -d pm_internship &>/dev/null; then
            log_success "PostgreSQL is ready"
            break
        fi
        retries=$((retries - 1))
        sleep 1
    done

    if [ $retries -eq 0 ]; then
        log_error "PostgreSQL failed to start"
        exit 1
    fi

    # Wait for Redis
    retries=30
    while [ $retries -gt 0 ]; do
        if docker exec pm-redis redis-cli ping &>/dev/null; then
            log_success "Redis is ready"
            break
        fi
        retries=$((retries - 1))
        sleep 1
    done

    # Wait for OpenSearch
    retries=60
    while [ $retries -gt 0 ]; do
        if curl -sf http://localhost:9200/_cluster/health &>/dev/null; then
            log_success "OpenSearch is ready"
            break
        fi
        retries=$((retries - 1))
        sleep 2
    done

    cd ../..
    log_success "Docker services started"
}

# ─────────────────────────────────────────────
# Database Migrations
# ─────────────────────────────────────────────

run_migrations() {
    log_info "Running database migrations..."

    cd backend
    source .venv/bin/activate
    alembic upgrade head
    cd ..

    log_success "Database migrations complete"
}

# ─────────────────────────────────────────────
# Seed Data
# ─────────────────────────────────────────────

seed_data() {
    log_info "Seeding test data..."

    cd backend
    source .venv/bin/activate
    cd ..
    python scripts/seed-data.py

    log_success "Test data seeded"
}

# ─────────────────────────────────────────────
# Start Application
# ─────────────────────────────────────────────

start_app() {
    log_info "Starting application services..."

    cd infrastructure/docker
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend frontend
    cd ../..

    log_success "Application services started"
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

main() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  PM Internship Smart Allocation Engine - Setup          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_prerequisites
    setup_env
    setup_python
    setup_node
    start_docker
    run_migrations
    seed_data
    start_app

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ Setup Complete!                                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BLUE}Backend:${NC}      http://localhost:8000"
    echo -e "  ${BLUE}Frontend:${NC}     http://localhost:3000"
    echo -e "  ${BLUE}API Docs:${NC}     http://localhost:8000/docs"
    echo -e "  ${BLUE}PgAdmin:${NC}      http://localhost:5050"
    echo -e "  ${BLUE}Temporal UI:${NC}  http://localhost:8081"
    echo -e "  ${BLUE}OpenSearch:${NC}   http://localhost:9200"
    echo ""
    echo -e "  ${YELLOW}Logs:${NC}  make dev-logs"
    echo -e "  ${YELLOW}Tests:${NC} make test"
    echo ""
}

main "$@"
