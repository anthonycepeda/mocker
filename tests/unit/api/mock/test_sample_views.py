from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.public.mock.models import MockResponse
from src.config import TestSettings

_settings = TestSettings()

SAMPLE_REQUEST_BODY = {
    "sample": {
        "id": "abc-123",
        "name": "trading-gateway",
        "owner": {"name": "Alice", "email": "alice@internal.com"},
        "status": "active",
    }
}

MOCK_RESPONSE = MockResponse(
    data={"id": "xyz-456", "name": "fake-name"},
    status_code=200,
    mocked_from="sample",
)


def client():
    app = create_app(_settings)
    return TestClient(app)


def test_mock_sample_endpoint_returns_200():
    with patch(
        "src.api.public.mock.views.build_mock_from_sample",
        return_value=MOCK_RESPONSE,
    ):
        response = client().post("/mock/sample", json=SAMPLE_REQUEST_BODY)
    assert response.status_code == 200


def test_mock_sample_endpoint_response_has_data():
    with patch(
        "src.api.public.mock.views.build_mock_from_sample",
        return_value=MOCK_RESPONSE,
    ):
        response = client().post("/mock/sample", json=SAMPLE_REQUEST_BODY)
    assert "data" in response.json()


def test_mock_sample_endpoint_mocked_from_is_sample():
    with patch(
        "src.api.public.mock.views.build_mock_from_sample",
        return_value=MOCK_RESPONSE,
    ):
        response = client().post("/mock/sample", json=SAMPLE_REQUEST_BODY)
    assert response.json()["mocked_from"] == "sample"


def test_mock_sample_endpoint_returns_422_on_missing_sample():
    response = client().post("/mock/sample", json={})
    assert response.status_code == 422
