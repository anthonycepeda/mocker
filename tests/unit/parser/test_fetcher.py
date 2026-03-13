import httpx
import pytest
import respx

from src.parser.fetcher import fetch_schema
from src.utils.exceptions import SchemaFetchError

SCHEMA_URL = "http://test-service/openapi.json"


@respx.mock
def test_fetch_schema_returns_dict(simple_schema):
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(200, json=simple_schema))
    result = fetch_schema(SCHEMA_URL)
    assert result == simple_schema


@respx.mock
def test_fetch_schema_raises_on_http_error():
    respx.get(SCHEMA_URL).mock(return_value=httpx.Response(404))
    with pytest.raises(SchemaFetchError, match="HTTP 404"):
        fetch_schema(SCHEMA_URL)


@respx.mock
def test_fetch_schema_raises_on_connection_error():
    respx.get(SCHEMA_URL).mock(side_effect=httpx.ConnectError("unreachable"))
    with pytest.raises(SchemaFetchError, match="unreachable"):
        fetch_schema(SCHEMA_URL)
