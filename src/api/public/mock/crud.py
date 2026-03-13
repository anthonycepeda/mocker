from src.api.public.mock.models import MockRequest, MockResponse
from src.generator import generate_mock
from src.parser.fetcher import fetch_schema
from src.parser.parser import parse_route
from src.utils.exceptions import SchemaParseError
from src.utils.registry import APP_REGISTRY


def _resolve_schema_url(request: MockRequest) -> str:
    """Resolve the schema URL from the request, preferring schema_url over app_name."""
    if request.schema_url:
        return request.schema_url
    url = APP_REGISTRY.get(request.app_name)
    if not url:
        raise SchemaParseError(f"Unknown app_name '{request.app_name}'. Not found in registry.")
    return url


def build_mock(request: MockRequest) -> MockResponse:
    """Orchestrate schema fetching, parsing, and mock data generation.

    Args:
        request: The MockRequest containing schema_url or app_name, endpoint, and method.

    Returns:
        A MockResponse with generated data, status code, and source URL.

    Raises:
        SchemaFetchError: If the schema URL is unreachable or returns an error.
        SchemaParseError: If the endpoint or method is not found in the schema, or app_name
            is not in the registry.
    """
    schema_url = _resolve_schema_url(request)
    schema = fetch_schema(schema_url)
    route = parse_route(schema, request.endpoint, request.method)
    data = generate_mock(route)

    return MockResponse(
        data=data,
        status_code=200,
        mocked_from=schema_url,
    )
