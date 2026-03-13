from fastapi import APIRouter, HTTPException

from src.api.public.mock.crud import build_mock
from src.api.public.mock.models import MockRequest, MockResponse
from src.utils.exceptions import SchemaFetchError, SchemaParseError

router = APIRouter()


@router.post("", response_model=MockResponse)
def mock_endpoint(request: MockRequest) -> MockResponse:
    """Generate a fake but schema-valid response for the given endpoint.

    Args:
        request: Schema URL, endpoint path, and HTTP method to mock.

    Returns:
        A MockResponse containing generated data and metadata.

    Raises:
        HTTPException 502: If the target schema URL is unreachable.
        HTTPException 422: If the endpoint or method is not found in the schema.
    """
    try:
        return build_mock(request)
    except SchemaFetchError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except SchemaParseError as e:
        raise HTTPException(status_code=422, detail=str(e))
