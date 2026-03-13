import httpx
import pytest
import respx

from src.api.public.mock.crud import build_mock
from src.api.public.mock.models import MockRequest, MockResponse
from src.config import TestSettings
from src.parser.fetcher import fetch_schema
from src.utils.exceptions import SchemaFetchError, SchemaParseError

_settings = TestSettings()
SCHEMA_URL = str(_settings.schema_url)


@pytest.fixture(autouse=True)
def clear_fetch_cache():
    fetch_schema.cache_clear()
    yield
    fetch_schema.cache_clear()


@respx.mock
def test_build_mock_returns_mock_response(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method)
    result = build_mock(request)
    assert isinstance(result, MockResponse)


@respx.mock
def test_build_mock_data_is_dict(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method)
    result = build_mock(request)
    assert isinstance(result.data, dict)


@respx.mock
def test_build_mock_status_code_is_200(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method)
    result = build_mock(request)
    assert result.status_code == 200


@respx.mock
def test_build_mock_mocked_from_is_schema_url(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method)
    result = build_mock(request)
    assert result.mocked_from == SCHEMA_URL


@respx.mock
def test_build_mock_raises_schema_fetch_error_on_unreachable():
    respx.get(SCHEMA_URL).mock(side_effect=httpx.ConnectError("unreachable"))
    request = MockRequest(schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method)
    with pytest.raises(SchemaFetchError):
        build_mock(request)


@respx.mock
def test_build_mock_raises_schema_parse_error_on_unknown_endpoint(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(schema_url=SCHEMA_URL, endpoint="/unknown", method="GET")
    with pytest.raises(SchemaParseError):
        build_mock(request)
