.PHONY: help install dev test clean run migrate seed docker-up docker-down

help:
	@echo "Property Listing Microservice - Available Commands:"
	@echo ""
	@echo "  make install     - Install production dependencies"
	@echo "  make dev         - Install development dependencies"
	@echo "  make run         - Run the development server"
	@echo "  make test        - Run tests with coverage"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed database with sample data"
	@echo "  make clean       - Clean up cache and temporary files"
	@echo "  make docker-up   - Start Docker containers"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make lint        - Run code linters"
	@echo "  make format      - Format code with black"
	@echo ""

install:
	pip install -r requirements.txt

dev: install
	pip install pytest pytest-asyncio pytest-cov pytest-mock black ruff

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

test:
	pytest

test-verbose:
	pytest -v -s

test-coverage:
	pytest --cov=app --cov-report=html --cov-report=term

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down:
	alembic downgrade -1

seed:
	python scripts/seed_data.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-rebuild:
	docker-compose up -d --build

docker-logs:
	docker-compose logs -f

lint:
	ruff check app/ tests/

format:
	black app/ tests/

format-check:
	black --check app/ tests/

db-shell:
	docker-compose exec postgres psql -U listing_user -d listing_db

# Development shortcuts
dev-setup: docker-up migrate seed
	@echo "✅ Development environment is ready!"
	@echo "Run 'make run' to start the server"

dev-reset: docker-down clean docker-up migrate seed
	@echo "✅ Development environment has been reset!"