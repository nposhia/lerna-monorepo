# Variables
DEVOPS_BASE_PATH = devops/local
DOCKER_COMPOSE = docker compose -f $(DEVOPS_BASE_PATH)/docker-compose.yml --env-file $(DEVOPS_BASE_PATH)/.env.docker
ENV_FILE = .env
ENV_DOCKER_FILE = $(DEVOPS_BASE_PATH)/.env.docker
CONTAINER_NAME = jeavio-backend
DB_CONTAINER = postgres
POSTGRES_DATABASE_USERNAME = $(shell grep POSTGRES_DATABASE_USERNAME $(ENV_DOCKER_FILE) | cut -d '=' -f2)
POSTGRES_DATABASE_NAME = $(shell grep POSTGRES_DATABASE_NAME $(ENV_DOCKER_FILE) | cut -d '=' -f2)

# Helper function for venv check
define check_venv
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "Error: Virtual environment is not activated!"; \
		echo "Please activate it first:"; \
		echo "source .venv/bin/activate  # For Unix/Linux/MacOS"; \
		echo "# OR"; \
		echo ".venv\\\Scripts\\\activate  # For Windows"; \
		exit 1; \
	fi
endef

# Check if env files exist
check-env-files:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "Error: $(ENV_FILE) not found. This file is required for the backend service."; \
		echo "Please create $(ENV_FILE) with appropriate application configuration."; \
		exit 1; \
	fi
	@if [ ! -f $(ENV_DOCKER_FILE) ]; then \
		echo "Error: $(ENV_DOCKER_FILE) not found. This file is required for the PostgreSQL service."; \
		echo "Please create $(ENV_DOCKER_FILE) with appropriate database configuration."; \
		exit 1; \
	fi

# Build commands
.PHONY: build
build: check-env-files
	$(DOCKER_COMPOSE) build

.PHONY: build-no-cache
build-no-cache: check-env-files
	$(DOCKER_COMPOSE) build --no-cache

# Docker commands
.PHONY: up up-d up-d-build down restart stop start
up: check-env-files
	$(DOCKER_COMPOSE) up

up-d: check-env-files
	$(DOCKER_COMPOSE) up -d

up-d-build: check-env-files
	$(DOCKER_COMPOSE) up -d --build

down:
	$(DOCKER_COMPOSE) down

restart: down up-d

stop:
	$(DOCKER_COMPOSE) stop

start:
	$(DOCKER_COMPOSE) start

# Logs
.PHONY: logs logs-app logs-db
logs:
	$(DOCKER_COMPOSE) logs -f

logs-app:
	$(DOCKER_COMPOSE) logs -f $(CONTAINER_NAME)

logs-db:
	$(DOCKER_COMPOSE) logs -f $(DB_CONTAINER)

# Clean up commands
.PHONY: clean clean-volumes clean-all
clean: down
	docker system prune -f

clean-volumes: down
	docker volume prune -f

clean-all: down
	docker system prune -af --volumes

# Database commands
.PHONY: db-shell db-migrate db-downgrade db-revision audit-sync
db-shell:
	$(DOCKER_COMPOSE) exec $(DB_CONTAINER) psql -U $(POSTGRES_DATABASE_USERNAME) -d $(POSTGRES_DATABASE_NAME)

db-migrate:
	$(call check_venv)
	alembic upgrade head

db-downgrade:
	$(call check_venv)
	alembic downgrade -1

db-revision:
	$(call check_venv)
	@if [ -z "$(message)" ]; then \
		echo "Error: Please provide a migration message using 'message=your_message'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(message)"

audit-sync:
	$(call check_venv)
	@echo "=== Synchronizing audit triggers ==="
	poetry run python scripts/postgresql_audit_sync.py

#data migration commands
.PHONY: data-migrate data-downgrade data-revision
data-migrate:
	$(call check_venv)
	poetry run python3 app/core/db/data_migrations/data_migrate.py upgrade

data-downgrade:
	$(call check_venv)
	if [ -z "$(revision_number)" ]; then \
		echo "Error: Please provide a migration revision number"; \
		exit 1; \
	fi
	poetry run python3 app/core/db/data_migrations/data_migrate.py downgrade $(revision_number)

data-revision:
	$(call check_venv)
	@if [ -z "$(message)" ]; then \
		echo "Error: Please provide a migration message using 'message=your_message'"; \
		exit 1; \
	fi
	poetry run python3 app/core/db/data_migrations/data_migrate.py create "$(message)"

data-history:
	$(call check_venv)
	poetry run python3 app/core/db/data_migrations/data_migrate.py history

data-current:
	$(call check_venv)
	poetry run python3 app/core/db/data_migrations/data_migrate.py current

# Container shell access
.PHONY: shell
shell:
	$(DOCKER_COMPOSE) exec $(CONTAINER_NAME) /bin/bash

# Status commands
.PHONY: ps status
ps:
	$(DOCKER_COMPOSE) ps

status:
	@echo "Container Status:"
	@docker ps --filter "name=$(CONTAINER_NAME)" --format "$(CONTAINER_NAME): {{.Status}}"
	@docker ps --filter "name=$(DB_CONTAINER)" --format "$(DB_CONTAINER): {{.Status}}"

# Development environment setup
.PHONY: setup install-deps run
setup:
	@echo "=== Setting up the project ==="
	@echo "1. Creating virtual environment..."
	python3.12 -m venv .venv
	@echo "\n2. To complete setup, run these commands:"
	@echo "source .venv/bin/activate  # For Unix/Linux/MacOS"
	@echo "# OR"
	@echo ".venv\\\Scripts\\\activate  # For Windows"
	@echo "\nThen run: make install-deps"

install-deps:
	$(call check_venv)
	@echo "=== Installing Poetry and dependencies ==="
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install --with dev
	@echo "\nSetup completed! You can now:"
	@echo "1. Run the application: make run"
	@echo "2. Start Docker containers: make up-d"
	@echo "3. Install pre-commit hooks: make install-pre-commit"

run:
	$(call check_venv)
	poetry run python -m main

# Pre-commit commands
.PHONY: install-pre-commit update-pre-commit lint
install-pre-commit:
	$(call check_venv)
	pre-commit install

update-pre-commit:
	$(call check_venv)
	pre-commit autoupdate

lint:
	$(call check_venv)
	pre-commit run --all-files

# Test commands
.PHONY: test test-unit test-integration test-e2e test-cov test-watch
test: check-env-files
	$(call check_venv)
	poetry run pytest -v tests/

test-unit: check-env-files
	$(call check_venv)
	poetry run pytest -v tests/unit/

test-integration: check-env-files
	$(call check_venv)
	poetry run pytest -v tests/integration/

test-e2e: check-env-files
	$(call check_venv)
	poetry run pytest -v tests/e2e/

test-cov: check-env-files
	$(call check_venv)
	poetry run pytest \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-report=xml \
		tests/

test-watch: check-env-files
	$(call check_venv)
	poetry run ptw --now tests/

# Environment variable commands
.PHONY: unset-env
unset-env:
	@echo "Unsetting environment variables..."
	@if [ -f $(ENV_FILE) ]; then \
		for var in $$(grep -v '^#' $(ENV_FILE) | cut -d '=' -f1); do \
			echo "Unsetting $$var"; \
			unset $$var; \
		done; \
		echo "Environment variables have been unset."; \
	else \
		echo "Warning: $(ENV_FILE) not found."; \
	fi

# Help command
.PHONY: help
help:
	@echo "Available commands:"
	@echo "\nDocker Commands:"
	@echo "  build           - Build Docker images"
	@echo "  build-no-cache - Build Docker images without cache"
	@echo "  up             - Start containers in foreground"
	@echo "  up-d           - Start containers in background"
	@echo "  up-d-build    - Start containers in background and build images"
	@echo "  down           - Stop and remove containers"
	@echo "  restart        - Restart all containers"
	@echo "  stop           - Stop containers"
	@echo "  start          - Start stopped containers"
	@echo "\nLogging Commands:"
	@echo "  logs           - View logs from all containers"
	@echo "  logs-app       - View application container logs"
	@echo "  logs-db        - View database container logs"
	@echo "\nCleanup Commands:"
	@echo "  clean          - Remove unused Docker resources"
	@echo "  clean-volumes  - Remove Docker volumes"
	@echo "  clean-all      - Remove all Docker resources"
	@echo "\nDatabase Commands:"
	@echo "  db-shell       - Access database shell"
	@echo "  db-migrate     - Run all pending database migrations"
	@echo "  db-downgrade   - Rollback the last database migration"
	@echo "  db-revision    - Create a new migration (use with message=your_message)"
	@echo "  audit-sync     - Synchronize audit triggers for all auditable tables"
	@echo "\nDevelopment Commands:"
	@echo "  shell          - Access application container shell"
	@echo "  ps             - List running containers"
	@echo "  status         - Show container status"
	@echo "  setup          - Create virtual environment and show next steps"
	@echo "  install-deps   - Install project dependencies (run after activating venv)"
	@echo "  run            - Run the main application"
	@echo "\nPre-commit Commands:"
	@echo "  install-pre-commit  - Install pre-commit hooks"
	@echo "  update-pre-commit   - Update pre-commit hooks to latest versions"
	@echo "  lint                - Run all pre-commit checks on all files"
	@echo "\nTest Commands:"
	@echo "  test             - Run all tests"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e        - Run end-to-end tests only"
	@echo "  test-cov        - Run tests with coverage report"
	@echo "  test-watch      - Run tests in watch mode (auto-rerun on file changes)"
	@echo "\nEnvironment Commands:"
	@echo "  unset-env      - Unset all environment variables defined in .env"

.DEFAULT_GOAL := help
