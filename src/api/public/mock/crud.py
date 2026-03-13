from src.api.public.mock.models import MockRequest, MockResponse
from src.generator import generate_mock
from src.parser.fetcher import fetch_schema
from src.parser.parser import parse_route


def build_mock(request: MockRequest) -> MockResponse:
    """Orchestrate schema fetching, parsing, and mock data generation.

    Args:
        request: The MockRequest containing schema_url, endpoint, and method.

    Returns:
        A MockResponse with generated data, status code, and source URL.

    Raises:
        SchemaFetchError: If the schema URL is unreachable or returns an error.
        SchemaParseError: If the endpoint or method is not found in the schema.
    """
    schema = fetch_schema(request.schema_url)
    route = parse_route(schema, request.endpoint, request.method)
    data = generate_mock(route)

    return MockResponse(
        data=data,
        status_code=200,
        mocked_from=request.schema_url,
    )
