from pydantic import BaseModel


class RouteDefinition(BaseModel):
    """Fully resolved schema for a single endpoint + method combination."""

    path: str
    method: str
    response_schema: dict
    status_code: int = 200
