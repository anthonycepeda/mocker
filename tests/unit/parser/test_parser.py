import pytest

from src.parser.models import RouteDefinition
from src.parser.parser import parse_route
from src.utils.exceptions import SchemaParseError


def test_parse_route_returns_route_definition(simple_schema):
    result = parse_route(simple_schema, "/services/{id}", "GET")
    assert isinstance(result, RouteDefinition)
    assert result.path == "/services/{id}"
    assert result.method == "get"


def test_parse_route_response_schema_is_resolved(simple_schema):
    result = parse_route(simple_schema, "/services/{id}", "GET")
    assert result.response_schema["type"] == "object"
    assert "id" in result.response_schema["properties"]


def test_parse_route_method_is_case_insensitive(simple_schema):
    result = parse_route(simple_schema, "/services/{id}", "get")
    assert result.method == "get"


def test_parse_route_raises_on_unknown_path(simple_schema):
    with pytest.raises(SchemaParseError, match="Path '/unknown'"):
        parse_route(simple_schema, "/unknown", "GET")


def test_parse_route_raises_on_unknown_method(simple_schema):
    with pytest.raises(SchemaParseError, match="Method 'POST'"):
        parse_route(simple_schema, "/services/{id}", "POST")
