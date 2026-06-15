.PHONY: dev build test lint migrate seed clean up down logs

# ──────────────────────────── Development ────────────────────────────

dev: ## Start all services in dev mode
	docker compose up --build -d
	@echo "✅ Services started. Backend: http://localhost:8000  Frontend: http://localhost:3000"

dev-backend: ## Start only backend + infra
	docker compose up --build -d postgres redis qdrant
	@sleep 3
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

up: ## Start services (no rebuild)
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Tail all service logs
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

# ──────────────────────────── Build ──────────────────────────────────

build: ## Build all Docker images
	docker compose build --no-cache

build-backend: ## Build backend image only
	docker compose build --no-cache backend

# ──────────────────────────── Testing ────────────────────────────────

test: ## Run backend tests
	cd backend && python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html --tb=short

# ──────────────────────────── Linting ────────────────────────────────

lint: ## Run linters
	cd backend && python -m ruff check app/
	cd backend && python -m mypy app/ --ignore-missing-imports

format: ## Auto-format code
	cd backend && python -m ruff format app/

# ──────────────────────────── Database ───────────────────────────────

migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new MSG="add users table")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed the database with sample data
	cd backend && python -m app.db.seed

# ──────────────────────────── Cleanup ────────────────────────────────

clean: ## Stop services and remove volumes
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "🧹 Cleaned up."

# ──────────────────────────── Help ───────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
