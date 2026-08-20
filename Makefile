# OverCoding — команды разработки.
# Требуется: docker, uv. Первый запуск: make setup && make up

SHELL := /bin/bash
COMPOSE := docker compose
BACKEND := cd backend &&

.DEFAULT_GOAL := help

.PHONY: help
help: ## показать список команд
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: .env ## подготовить окружение: .env + зависимости
	$(BACKEND) uv sync --python 3.12 --extra dev
	@echo "Готово. Дальше: make up"

.env: ## создать .env из шаблона со сгенерированным SECRET_KEY
	@test -f .env || { \
	  sed "s|^SECRET_KEY=.*|SECRET_KEY=$$(openssl rand -hex 32)|" .env.example > .env; \
	  echo "Создан .env со сгенерированным SECRET_KEY"; }

.PHONY: up
up: .env ## поднять базу, Redis и API
	$(COMPOSE) up -d --build db redis api
	@echo "API: http://localhost:8000/docs"

.PHONY: down
down: ## остановить всё
	$(COMPOSE) down

.PHONY: clean
clean: ## остановить и УДАЛИТЬ данные базы (необратимо)
	$(COMPOSE) down -v

.PHONY: logs
logs: ## логи API
	$(COMPOSE) logs -f api

.PHONY: shell
shell: ## оболочка внутри контейнера API
	$(COMPOSE) exec api bash

.PHONY: psql
psql: ## psql к локальной базе
	$(COMPOSE) exec db psql -U overcoding -d overcoding

.PHONY: migrate
migrate: ## применить миграции
	$(COMPOSE) exec api alembic upgrade head

.PHONY: downgrade
downgrade: ## откатить последнюю миграцию
	$(COMPOSE) exec api alembic downgrade -1

.PHONY: revision
revision: ## новая миграция: make revision m="описание"
	@test -n "$(m)" || { echo "Нужно: make revision m=\"описание\""; exit 1; }
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(m)"

.PHONY: test
test: ## тесты
	$(BACKEND) uv run pytest

.PHONY: lint
lint: ## линтер и проверка типов
	$(BACKEND) uv run ruff check .
	$(BACKEND) uv run ruff format --check .
	$(BACKEND) uv run mypy .

.PHONY: fmt
fmt: ## отформатировать код
	$(BACKEND) uv run ruff format .
	$(BACKEND) uv run ruff check --fix .

.PHONY: content
content: ## загрузить курсы из репозитория в базу (пересоздаёт курс)
	$(BACKEND) uv run python -c "from app.db.session import SessionLocal; from app.content.loader import load_all; [print(s) for s in load_all(SessionLocal())]"

.PHONY: content-verify
content-verify: ## прогнать эталонные решения через песочницу (нужна сеть, минуты)
	$(BACKEND) RUN_CONTENT_INTEGRATION=1 uv run pytest tests/test_content.py -q -k reference

.PHONY: check
check: lint test ## всё, что проверяет CI
