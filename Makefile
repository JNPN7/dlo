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

build:
	uv build

ui:
	@npm run dev --prefix src/dlo/ui

ui-build:
	@npm run build --prefix src/dlo/ui

ui-start:
	@npm run start --prefix src/dlo/ui
