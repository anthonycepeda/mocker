import pytest


@pytest.fixture
def simple_schema() -> dict:
    """Minimal OpenAPI schema with a single GET /accounts/{id} endpoint."""
    return {
        "openapi": "3.1.0",
        "paths": {
            "/accounts/{id}": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Account"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Account": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "balance": {"type": "number"},
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
