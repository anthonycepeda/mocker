from src.api.public.mock.models import MockRequest, MockResponse, SampleRequest
from src.config import get_settings
from src.generator import generate_mock
from src.generator.sampler import generate_from_sample
from src.parser.fetcher import fetch_schema
from src.parser.parser import parse_route
from src.utils.custom_hints import load_custom_hints, resolve_hints_for_app
from src.utils.exceptions import SchemaParseError
from src.utils.logger import logger_config
from src.utils.registry import APP_REGISTRY

logger = logger_config(__name__)


def _resolve_custom_hints(app_name: str | None = None) -> dict[str, list] | None:
    """Load and resolve custom hints for the given app name.

    Returns None if no custom hints file is configured.
    """
    path = get_settings().custom_hints_path
    if path is None:
        return None
    raw = load_custom_hints(path)
    return resolve_hints_for_app(raw, app_name)


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
    logger.info("mock requested", extra={"endpoint": request.endpoint, "method": request.method})
    schema = fetch_schema(schema_url)
    route = parse_route(schema, request.endpoint, request.method)
    data = generate_mock(
        route,
        custom_hints=_resolve_custom_hints(request.app_name),
        overrides=request.overrides,
    )
    logger.info("mock generated", extra={"endpoint": request.endpoint, "method": request.method})

    return MockResponse(
        data=data,
        status_code=route.status_code,
        mocked_from=schema_url,
    )


def build_mock_from_sample(request: SampleRequest) -> MockResponse:
    """Generate fake data by walking the shape of a caller-provided response sample.

    Args:
        request: A SampleRequest containing the response dict to use as a template.

    Returns:
        A MockResponse with regenerated data preserving the sample's structure.
    """
    data = generate_from_sample(request.sample, custom_hints=_resolve_custom_hints())
    return MockResponse(data=data, status_code=200, mocked_from="sample")
