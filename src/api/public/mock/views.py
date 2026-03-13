from fastapi import APIRouter, HTTPException

from src.api.public.mock.crud import build_mock, build_mock_from_sample
from src.api.public.mock.models import MockRequest, MockResponse, SampleRequest
from src.utils.exceptions import SchemaFetchError, SchemaParseError

router = APIRouter()


@router.post("/schema", response_model=MockResponse)
def mock_schema_endpoint(request: MockRequest) -> MockResponse:
    """Generate a fake but schema-valid response by fetching the OpenAPI schema.

    Args:
        request: Schema URL or app name, endpoint path, and HTTP method to mock.

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


@router.post("/sample", response_model=MockResponse)
def mock_sample_endpoint(request: SampleRequest) -> MockResponse:
    """Generate fake data by regenerating values from a caller-provided response sample.

    Preserves the shape of the sample — all values are replaced with fresh fake data.
    Semantic hints (email, iban, name, etc.) are applied where field names match.

    Args:
        request: A dict representing a real or representative response to use as a template.

    Returns:
        A MockResponse with regenerated data matching the sample's structure.
    """
    return build_mock_from_sample(request)
