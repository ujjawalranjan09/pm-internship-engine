# ============================================================
# Makefile - PM Internship Smart Allocation Engine
# ============================================================

.PHONY: help dev dev-down test lint build deploy migrate seed clean setup \
        backend-test frontend-test backend-lint frontend-lint \
        docker-build docker-up docker-down logs health-check backup

# Default target
.DEFAULT_GOAL := help

# Colors
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Docker Compose files
COMPOSE_FILE := infrastructure/docker/docker-compose.yml
COMPOSE_DEV_FILE := infrastructure/docker/docker-compose.dev.yml
COMPOSE := docker compose -f $(COMPOSE_FILE)
COMPOSE_DEV := docker compose -f $(COMPOSE_FILE) -f $(COMPOSE_DEV_FILE)

# ─────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────
help: ## Show this help message
	@echo "$(BLUE)PM Internship Smart Allocation Engine$(RESET)"
	@echo "$(BLUE)======================================$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# ─────────────────────────────────────────────
# Development
# ─────────────────────────────────────────────
dev: ## Start development environment with hot-reload
	@echo "$(BLUE)Starting development environment...$(RESET)"
	$(COMPOSE_DEV) up -d
	@echo "$(GREEN)✓ Development environment started$(RESET)"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  PgAdmin:  http://localhost:5050"
	@echo "  Temporal: http://localhost:8081"

dev-down: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	$(COMPOSE_DEV) down
	@echo "$(GREEN)✓ Development environment stopped$(RESET)"

dev-logs: ## Show development logs
	$(COMPOSE_DEV) logs -f

dev-rebuild: ## Rebuild and restart development containers
	$(COMPOSE_DEV) up -d --build

# ─────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────
test: backend-test frontend-test ## Run all tests

backend-test: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(RESET)"
	cd backend && python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
	@echo "$(GREEN)✓ Backend tests complete$(RESET)"

frontend-test: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(RESET)"
	cd frontend && npm test
	@echo "$(GREEN)✓ Frontend tests complete$(RESET)"

test-watch: ## Run backend tests in watch mode
	cd backend && python -m pytest tests/ -v --tb=short -f

test-coverage: ## Run tests with coverage report
	cd backend && python -m pytest tests/ --cov=app --cov-report=html:htmlcov --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report: backend/htmlcov/index.html$(RESET)"

# ─────────────────────────────────────────────
# Linting
# ─────────────────────────────────────────────
lint: backend-lint frontend-lint ## Run all linters

backend-lint: ## Run backend linters (ruff + mypy)
	@echo "$(BLUE)Running backend linters...$(RESET)"
	cd backend && ruff check .
	cd backend && ruff format --check .
	cd backend && mypy app/ --config-file pyproject.toml
	@echo "$(GREEN)✓ Backend linting complete$(RESET)"

frontend-lint: ## Run frontend linters (eslint + tsc)
	@echo "$(BLUE)Running frontend linters...$(RESET)"
	cd frontend && npm run lint
	cd frontend && npx tsc --noEmit
	@echo "$(GREEN)✓ Frontend linting complete$(RESET)"

lint-fix: ## Auto-fix linting issues
	cd backend && ruff check --fix .
	cd backend && ruff format .
	cd frontend && npm run lint -- --fix

# ─────────────────────────────────────────────
# Building
# ─────────────────────────────────────────────
build: docker-build ## Build all Docker images

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(RESET)"
	docker build -t pm-internship-backend:latest \
		-f infrastructure/docker/Dockerfile.backend \
		--target production .
	docker build -t pm-internship-frontend:latest \
		-f infrastructure/docker/Dockerfile.frontend \
		--target production .
	@echo "$(GREEN)✓ Docker images built$(RESET)"

docker-up: ## Start production-like Docker environment
	$(COMPOSE) up -d
	@echo "$(GREEN)✓ Production environment started$(RESET)"

docker-down: ## Stop Docker environment
	$(COMPOSE) down

# ─────────────────────────────────────────────
# Deployment
# ─────────────────────────────────────────────
deploy: ## Deploy to current environment
	@echo "$(BLUE)Deploying...$(RESET)"
	./scripts/deploy.sh
	@echo "$(GREEN)✓ Deployment complete$(RESET)"

deploy-staging: ## Deploy to staging
	@echo "$(BLUE)Deploying to staging...$(RESET)"
	cd infrastructure/terraform && terraform workspace select staging
	cd infrastructure/terraform && terraform apply -var-file=staging.tfvars
	@echo "$(GREEN)✓ Staging deployment complete$(RESET)"

deploy-production: ## Deploy to production
	@echo "$(RED)⚠ Deploying to production...$(RESET)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	cd infrastructure/terraform && terraform workspace select production
	cd infrastructure/terraform && terraform apply -var-file=production.tfvars
	@echo "$(GREEN)✓ Production deployment complete$(RESET)"

# ─────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────
migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(RESET)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(RESET)"

migrate-create: ## Create a new migration (usage: make migrate-create NAME="add candidates table")
	@echo "$(BLUE)Creating migration: $(NAME)...$(RESET)"
	cd backend && alembic revision --autogenerate -m "$(NAME)"
	@echo "$(GREEN)✓ Migration created$(RESET)"

migrate-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(RESET)"
	cd backend && alembic downgrade -1
	@echo "$(GREEN)✓ Rollback complete$(RESET)"

seed: ## Seed database with test data
	@echo "$(BLUE)Seeding database...$(RESET)"
	python scripts/seed-data.py
	@echo "$(GREEN)✓ Database seeded$(RESET)"

db-shell: ## Open PostgreSQL shell
	docker exec -it pm-postgres psql -U pm_admin -d pm_internship

# ─────────────────────────────────────────────
# Infrastructure
# ─────────────────────────────────────────────
tf-init: ## Initialize Terraform
	cd infrastructure/terraform && terraform init

tf-plan: ## Plan Terraform changes
	cd infrastructure/terraform && terraform plan -var-file=$(ENV).tfvars

tf-apply: ## Apply Terraform changes
	cd infrastructure/terraform && terraform apply -var-file=$(ENV).tfvars

tf-destroy: ## Destroy Terraform resources
	@echo "$(RED)⚠ Destroying infrastructure...$(RESET)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	cd infrastructure/terraform && terraform destroy -var-file=$(ENV).tfvars

# ─────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────
setup: ## One-command local setup
	@echo "$(BLUE)Running setup...$(RESET)"
	./scripts/setup.sh
	@echo "$(GREEN)✓ Setup complete$(RESET)"

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/coverage.xml
	rm -rf frontend/.next frontend/out
	@echo "$(GREEN)✓ Clean complete$(RESET)"

logs: ## Show all container logs
	$(COMPOSE) logs -f

health-check: ## Run health checks on all services
	@echo "$(BLUE)Running health checks...$(RESET)"
	./scripts/health-check.sh

backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(RESET)"
	./scripts/backup.sh
	@echo "$(GREEN)✓ Backup complete$(RESET)"

# ─────────────────────────────────────────────
# Quick Commands
# ─────────────────────────────────────────────
shell-backend: ## Open shell in backend container
	docker exec -it pm-backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker exec -it pm-frontend /bin/sh

redis-cli: ## Open Redis CLI
	docker exec -it pm-redis redis-cli

opensearch-status: ## Check OpenSearch cluster status
	curl -s http://localhost:9200/_cluster/health?pretty
