# Common developer commands for QuickGigs.
# Run `make help` to see what's available.

PYTHON ?= python
MANAGE = $(PYTHON) manage.py

.PHONY: help install dev run migrate makemigrations shell test lint format check \
        clean docker-build docker-up docker-down docker-logs collectstatic superuser

help:  ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make <target>\n\nTargets:\n"} \
	    /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:  ## Install runtime + dev dependencies into the current Python env.
	pip install -U pip
	pip install -r requirements.txt -r requirements-dev.txt

dev: install  ## Bootstrap a local dev environment (install + migrate).
	$(MANAGE) migrate

run:  ## Run the Django dev server on http://localhost:8000.
	$(MANAGE) runserver 0.0.0.0:8000

migrate:  ## Apply database migrations.
	$(MANAGE) migrate

makemigrations:  ## Generate migrations from current models.
	$(MANAGE) makemigrations

shell:  ## Open a Django shell.
	$(MANAGE) shell

superuser:  ## Create an admin superuser.
	$(MANAGE) createsuperuser

collectstatic:  ## Collect static assets into STATIC_ROOT.
	$(MANAGE) collectstatic --noinput

test:  ## Run the test suite.
	pytest

lint:  ## Lint the codebase with ruff.
	ruff check .

format:  ## Format the codebase with ruff.
	ruff format .

check: lint  ## Run all static checks.
	$(MANAGE) check --deploy --fail-level WARNING || true

clean:  ## Remove caches and build artifacts (does not touch your database).
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	rm -rf .coverage htmlcov staticfiles

docker-build:  ## Build the Docker image.
	docker compose build

docker-up:  ## Start the dev stack (web + Postgres).
	docker compose up

docker-down:  ## Stop the dev stack.
	docker compose down

docker-logs:  ## Tail logs from the web service.
	docker compose logs -f web
