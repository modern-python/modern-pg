default: install lint build test

down:
    docker compose down --remove-orphans

sh:
    docker compose run --service-ports application bash

test *args: down && down
    docker compose run application uv run --no-sync pytest {{ args }}

build:
    docker compose build application

install:
    uv lock --upgrade
    uv sync --all-extras --frozen

lint:
    uv run --frozen ruff format
    uv run --frozen ruff check --fix
    uv run --frozen mypy .

lint-ci:
    uv run --frozen ruff format --check
    uv run --frozen ruff check --no-fix
    uv run --frozen mypy .

publish:
    rm -rf dist
    uv build
    uv publish --token $PYPI_TOKEN
