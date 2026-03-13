COMMIT_SHA  := $(shell git rev-parse --short HEAD)
IMAGE       := mocker:$(COMMIT_SHA)

.PHONY: install format lint test run run-reload \
        docker-build docker-run \
        helm-dev helm-staging helm-production helm-diff helm-destroy

install:
	uv sync

format:
	uv run ruff format .
	uv run ruff check . --fix

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

run:
	uv run python asgi.py

run-reload:
	uv run uvicorn asgi:app --host 0.0.0.0 --port 8080 --reload

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm -p 8080:8080 $(IMAGE)

helm-dev:
	COMMIT_SHA=$(COMMIT_SHA) helmfile --file deploy/helmfile.yaml --environment development apply

helm-staging:
	COMMIT_SHA=$(COMMIT_SHA) helmfile --file deploy/helmfile.yaml --environment staging apply

helm-production:
	COMMIT_SHA=$(COMMIT_SHA) helmfile --file deploy/helmfile.yaml --environment production apply

helm-diff:
	COMMIT_SHA=$(COMMIT_SHA) helmfile --file deploy/helmfile.yaml --environment $(ENV) diff

helm-destroy:
	helmfile --file deploy/helmfile.yaml --environment $(ENV) destroy
