from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.public.mock.models import MockResponse
from src.config import TestSettings
from src.utils.exceptions import SchemaFetchError, SchemaParseError

_settings = TestSettings()
SCHEMA_URL = str(_settings.schema_url)

MOCK_REQUEST_BODY = {
    "schema_url": SCHEMA_URL,
    "endpoint": _settings.endpoint,
    "method": _settings.method,
}

MOCK_RESPONSE = MockResponse(
    data={"id": 1, "name": "Test"},
    status_code=200,
    mocked_from=SCHEMA_URL,
)


@pytest.fixture
def client():
    app = create_app(_settings)
    return TestClient(app)


def test_mock_endpoint_returns_200(client):
    with patch("src.api.public.mock.views.build_mock", return_value=MOCK_RESPONSE):
        response = client.post("/mock", json=MOCK_REQUEST_BODY)
    assert response.status_code == 200


def test_mock_endpoint_response_has_data(client):
    with patch("src.api.public.mock.views.build_mock", return_value=MOCK_RESPONSE):
        response = client.post("/mock", json=MOCK_REQUEST_BODY)
    assert "data" in response.json()


def test_mock_endpoint_response_has_status_code(client):
    with patch("src.api.public.mock.views.build_mock", return_value=MOCK_RESPONSE):
        response = client.post("/mock", json=MOCK_REQUEST_BODY)
    assert response.json()["status_code"] == 200


def test_mock_endpoint_response_has_mocked_from(client):
    with patch("src.api.public.mock.views.build_mock", return_value=MOCK_RESPONSE):
        response = client.post("/mock", json=MOCK_REQUEST_BODY)
    assert response.json()["mocked_from"] == SCHEMA_URL


def test_mock_endpoint_returns_502_on_schema_fetch_error(client):
    with patch("src.api.public.mock.views.build_mock", side_effect=SchemaFetchError("unreachable")):
        response = client.post("/mock", json=MOCK_REQUEST_BODY)
    assert response.status_code == 502


def test_mock_endpoint_returns_422_on_schema_parse_error(client):
    invalid_body = {"schema_url": SCHEMA_URL, "endpoint": "/unknown", "method": "GET"}
    with patch("src.api.public.mock.views.build_mock", side_effect=SchemaParseError("unknown")):
        response = client.post("/mock", json=invalid_body)
    assert response.status_code == 422
