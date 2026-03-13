from pydantic import BaseModel, ConfigDict


class MockRequest(BaseModel):
    """Request body for the POST /mock endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schema_url": "http://service-registry/openapi.json",
                "endpoint": "/services/{id}",
                "method": "GET",
            }
        }
    )

    schema_url: str
    endpoint: str
    method: str


class MockResponse(BaseModel):
    """Response envelope for the POST /mock endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": {
                    "id": "a3f2c1d0-4e5b-4c6d-8f7e-1a2b3c4d5e6f",
                    "name": "trading-gateway",
                    "region": "EMEA",
                    "ecosystem": "TRADECORE",
                    "status": "active",
                    "owner": {
                        "name": "Alice Martin",
                        "email": "alice.martin@internal.example.com",
                    },
                },
                "status_code": 200,
                "mocked_from": "http://service-registry/openapi.json",
            }
        }
    )

    data: dict
    status_code: int
    mocked_from: str
