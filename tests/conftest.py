import pytest


@pytest.fixture
def simple_schema() -> dict:
    """Minimal OpenAPI schema with a single GET /services/{id} endpoint."""
    return {
        "openapi": "3.1.0",
        "paths": {
            "/services/{id}": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Service"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Service": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "region": {"type": "string"},
                        "ecosystem": {"type": "string"},
                        "status": {"type": "string"},
                        "owner": {"$ref": "#/components/schemas/Owner"},
                    },
                },
                "Owner": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                },
            }
        },
    }
