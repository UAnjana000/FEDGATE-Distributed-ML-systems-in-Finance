SHELL := /bin/sh

.PHONY: up down logs test lint format fl-round seed

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

test:
	docker compose run --rm api-gateway pytest -q

lint:
	docker compose run --rm api-gateway ruff check .

format:
	docker compose run --rm api-gateway ruff format .

fl-round:
	curl -X POST http://localhost:8002/fl/start \
		-H "Content-Type: application/json" \
		-d '{"num_clients":3,"num_rounds":2}'

seed:
	curl -X POST http://localhost:8000/borrowers/seed
