# Mocker

A FastAPI service that generates realistic, schema-valid mock data from internal FastAPI endpoints. Point your tests at Mocker instead of the real service — no test code changes required.

## Architecture

```mermaid
flowchart LR
    A[POST /mock] --> B[parser/\nfetch + resolve schema]
    B --> C[generator/\nproduce fake data]
    C --> D[JSON response]
```

## The Problem

Writing mock fixtures by hand is tedious and drifts from the real schema over time. Mocker reads the OpenAPI schema directly from your service and generates realistic fake responses automatically.

**Before** — your tests call the real service (or you maintain hand-rolled mocks):
```python
response = httpx.get("http://payments-api/accounts/123")
```

**After** — point `BASE_URL` at Mocker. No other changes:
```python
response = httpx.get("http://localhost:8080/mock")  # returns fake but schema-valid data
```

## Getting Started

```bash
# Install dependencies
uv sync

# Run the API
uv run uvicorn src.api.main:app --reload
```

## Usage

```bash
POST /mock
Content-Type: application/json

{
  "schema_url": "http://payments-api/openapi.json",
  "endpoint": "/accounts/{id}",
  "method": "GET"
}
```

**Response:**
```json
{
  "id": "a3f2c1d0-...",
  "balance": 4821.53,
  "owner": {
    "name": "Jane Smith",
    "email": "jane.smith@example.com"
  }
}
```

Mocker fetches the OpenAPI schema from `schema_url`, resolves all `$ref` pointers, and returns a fake but structurally valid response for the requested endpoint and method.

## Running Tests

```bash
# All tests
uv run pytest

# Single file
uv run pytest tests/unit/parser/test_parser.py

# Single test
uv run pytest -k "test_parse_route_returns_route_definition"
```

## Roadmap

- [x] Phase 1 — Parser: fetch OpenAPI schema, resolve `$ref`s, extract `RouteDefinition`
- [ ] Phase 2 — Generator: walk `RouteDefinition` and produce fake data (Faker + semantic hints)
- [ ] Phase 3 — API: `POST /mock` endpoint wiring parser + generator
- [ ] Phase 4 — Semantic hints: field name inference (`email`, `iban`, `date`, `amount`)
- [ ] Phase 5 — Schema caching: avoid re-fetching on every request
- [ ] Phase 6 — Stub server: mirror all routes from a target service (drop-in replacement mode)
