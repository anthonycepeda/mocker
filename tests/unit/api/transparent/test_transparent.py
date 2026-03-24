import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.config import TestSettings, get_settings
from src.parser.fetcher import fetch_schema
from src.utils.registry import APP_REGISTRY

_settings = TestSettings()
SCHEMA_URL = str(_settings.schema_url)
APP_NAME = "test-service"


@pytest.fixture(autouse=True)
def clear_fetch_cache():
    fetch_schema.cache_clear()
    yield
    fetch_schema.cache_clear()


@pytest.fixture
def client():
    """Test client with test-service registered in APP_REGISTRY."""
    APP_REGISTRY[APP_NAME] = SCHEMA_URL
    app = create_app(get_settings())
    yield TestClient(app)
    APP_REGISTRY.pop(APP_NAME, None)


@respx.mock
def test_transparent_get_returns_mock_data(client, simple_schema):
    """GET /{app_name}/{path} returns generated mock data."""
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    response = client.get(f"/{APP_NAME}/services/abc-123")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@respx.mock
def test_transparent_post_returns_schema_status_code(client):
    """POST /{app_name}/{path} returns the status code from the schema."""
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/services": {
                "post": {
                    "responses": {
                        "201": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"id": {"type": "string"}},
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    }
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=schema))
    response = client.post(f"/{APP_NAME}/services")
    assert response.status_code == 201


@respx.mock
def test_transparent_path_preserved(client, simple_schema):
    """The path after the app_name prefix is passed as the endpoint verbatim."""
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    # /services/{id} is the endpoint defined in simple_schema
    response = client.get(f"/{APP_NAME}/services/abc-123")
    assert response.status_code == 200


def test_transparent_unknown_app_returns_422(client):
    """An unregistered app_name returns a structured 422 error."""
    response = client.get("/unknown-app/users/123")
    assert response.status_code == 422
