CONTAINER_NAME:= 'boilerplate-fastapi'
IMAGE_NAME:= 'boilerplate-fastapi'

run: 
	@echo TODO

dev:
	@echo TODO

install:
	@uv sync

install-dev:
	@uv sync --group dev

lint:
	uv run ruff check

lint-fix:
	uv run ruff check --fix

format:
	uv run ruff format
