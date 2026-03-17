import httpx
import pytest
import respx

from src.api.public.mock.crud import build_mock
from src.api.public.mock.models import MockRequest, MockResponse
from src.config import TestSettings
from src.parser.fetcher import fetch_schema
from src.utils.exceptions import SchemaFetchError, SchemaParseError
from src.utils.registry import APP_REGISTRY

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
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert isinstance(result, MockResponse)


@respx.mock
def test_build_mock_data_is_dict_for_object_schema(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert isinstance(result.data, dict)


@respx.mock
def test_build_mock_data_is_list_for_array_schema(simple_schema):
    array_schema = {
        **simple_schema,
        "paths": {
            _settings.endpoint: {
                _settings.method.lower(): {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Service"},
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    }
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=array_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert isinstance(result.data, list)


@respx.mock
def test_build_mock_status_code_is_200(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert result.status_code == 200


@respx.mock
def test_build_mock_mocked_from_is_schema_url(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert result.mocked_from == SCHEMA_URL


@respx.mock
def test_build_mock_raises_schema_fetch_error_on_unreachable():
    respx.get(SCHEMA_URL).mock(side_effect=httpx.ConnectError("unreachable"))
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    with pytest.raises(SchemaFetchError):
        build_mock(request)


@respx.mock
def test_build_mock_raises_schema_parse_error_on_unknown_endpoint(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(schema_url=SCHEMA_URL, endpoint="/unknown", method="GET")
    with pytest.raises(SchemaParseError):
        build_mock(request)


@respx.mock
def test_build_mock_resolves_app_name_to_schema_url(simple_schema):
    registered_url = APP_REGISTRY["service-registry"]
    respx.get(registered_url).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        app_name="service-registry", endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert result.mocked_from == registered_url


@respx.mock
def test_build_mock_schema_url_overrides_app_name(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL,
        app_name="service-registry",
        endpoint=_settings.endpoint,
        method=_settings.method,
    )
    result = build_mock(request)
    assert result.mocked_from == SCHEMA_URL


def test_build_mock_raises_on_unknown_app_name():
    request = MockRequest(
        app_name="unknown-app", endpoint=_settings.endpoint, method=_settings.method
    )
    with pytest.raises(SchemaParseError, match="unknown-app"):
        build_mock(request)


def test_mock_request_raises_if_neither_schema_url_nor_app_name():
    with pytest.raises(ValueError, match="Either"):
        MockRequest(endpoint=_settings.endpoint, method=_settings.method)


@respx.mock
def test_build_mock_status_code_from_schema(simple_schema):
    schema_201 = {
        **simple_schema,
        "paths": {
            _settings.endpoint: {
                _settings.method.lower(): {
                    "responses": {
                        "201": simple_schema["paths"][_settings.endpoint][
                            _settings.method.lower()
                        ]["responses"]["200"]
                    }
                }
            }
        },
    }
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=schema_201))
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert result.status_code == 201


@respx.mock
def test_build_mock_overrides_echo_matching_field(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL,
        endpoint=_settings.endpoint,
        method=_settings.method,
        overrides={"region": "EMEA"},
    )
    result = build_mock(request)
    assert result.data["region"] == "EMEA"


@respx.mock
def test_build_mock_overrides_unknown_keys_ignored(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL,
        endpoint=_settings.endpoint,
        method=_settings.method,
        overrides={"nonexistent_field": "value"},
    )
    result = build_mock(request)
    assert "nonexistent_field" not in result.data


@respx.mock
def test_build_mock_without_overrides_unchanged(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    request = MockRequest(
        schema_url=SCHEMA_URL, endpoint=_settings.endpoint, method=_settings.method
    )
    result = build_mock(request)
    assert isinstance(result.data, dict)
