from pydantic import BaseModel, ConfigDict, model_validator


class MockRequest(BaseModel):
    """Request body for the POST /mock/schema endpoint.

    Provide either `schema_url` or `app_name` (not both required).
    If both are given, `schema_url` takes precedence.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "app_name": "service-registry",
                "schema_url": "http://service-registry/openapi.json",
                "endpoint": "/services/{id}",
                "method": "GET",
            }
        }
    )

    schema_url: str | None = None
    app_name: str | None = None
    endpoint: str
    method: str

    @model_validator(mode="after")
    def require_schema_url_or_app_name(self) -> "MockRequest":
        if not self.schema_url and not self.app_name:
            raise ValueError("Either 'schema_url' or 'app_name' must be provided.")
        return self


class SampleRequest(BaseModel):
    """Request body for the POST /mock/sample endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sample": {
                    "id": "a3f2c1d0-4e5b-4c6d-8f7e-1a2b3c4d5e6f",
                    "name": "payment-gateway",
                    "owner": {"name": "Jane Smith", "email": "jane.smith@example.com"},
                    "status": "active",
                }
            }
        }
    )

    sample: dict


class MockResponse(BaseModel):
    """Response envelope for the POST /mock/schema and POST /mock/sample endpoints."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": {
                    "id": "a3f2c1d0-4e5b-4c6d-8f7e-1a2b3c4d5e6f",
                    "name": "payment-gateway",
                    "region": "EMEA",
                    "ecosystem": "CORE",
                    "status": "active",
                    "owner": {
                        "name": "Jane Smith",
                        "email": "jane.smith@example.com",
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
