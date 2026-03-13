import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.config import TestSettings


@pytest.fixture
def client():
    app = create_app(TestSettings())
    return TestClient(app)


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_status_ok(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_healthz_returns_200(client):
    response = client.get("/healthz")
    assert response.status_code == 200


def test_healthz_returns_empty(client):
    response = client.get("/healthz")
    assert response.json() == {}


def test_ready_returns_200(client):
    response = client.get("/ready")
    assert response.status_code == 200


def test_ready_returns_empty(client):
    response = client.get("/ready")
    assert response.json() == {}
