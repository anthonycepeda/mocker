from pydantic import BaseModel


class MockRequest(BaseModel):
    """Request body for the POST /mock endpoint."""

    schema_url: str
    endpoint: str
    method: str


class MockResponse(BaseModel):
    """Response envelope for the POST /mock endpoint."""

    data: dict
    status_code: int
    mocked_from: str
