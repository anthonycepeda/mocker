import pytest

from src.parser.models import RouteDefinition
from src.parser.parser import _resolve_path_template, parse_route
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


def test_parse_route_status_code_from_schema(simple_schema):
    result = parse_route(simple_schema, "/services/{id}", "GET")
    assert result.status_code == 200


def test_parse_route_picks_non_200_status_code():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "post": {
                    "responses": {
                        "201": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"username": {"type": "string"}},
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
    }
    result = parse_route(schema, "/users", "POST")
    assert result.status_code == 201


def test_parse_route_picks_first_2xx_when_multiple():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "post": {
                    "responses": {
                        "202": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"username": {"type": "string"}},
                                    }
                                }
                            }
                        },
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"id": {"type": "string"}},
                                    }
                                }
                            }
                        },
                    }
                }
            }
        },
    }
    result = parse_route(schema, "/users", "POST")
    assert result.status_code == 200  # sorted picks 200 before 202


def test_parse_route_raises_when_no_2xx():
    schema = {
        "openapi": "3.1.0",
        "paths": {
            "/users": {
                "post": {
                    "responses": {
                        "400": {"description": "Bad request"},
                    }
                }
            }
        },
    }
    with pytest.raises(SchemaParseError, match="No 2xx"):
        parse_route(schema, "/users", "POST")


def test_parse_route_strips_query_string(simple_schema):
    """/services/{id}?foo=bar resolves to /services/{id} ignoring the query string."""
    result = parse_route(simple_schema, "/services/{id}?foo=bar", "GET")
    assert isinstance(result, RouteDefinition)


def test_parse_route_matches_concrete_path_to_template(simple_schema):
    """Concrete path /services/abc-123 resolves to template /services/{id}."""
    result = parse_route(simple_schema, "/services/abc-123", "GET")
    assert isinstance(result, RouteDefinition)


def test_resolve_path_template_exact_match():
    paths = {"/services/{id}": {}, "/users": {}}
    assert _resolve_path_template(paths, "/services/{id}") == "/services/{id}"


def test_resolve_path_template_concrete_path():
    paths = {"/services/{id}": {}}
    assert _resolve_path_template(paths, "/services/abc-123") == "/services/{id}"


def test_resolve_path_template_multi_segment():
    paths = {"/orgs/{org_id}/users/{user_id}": {}}
    assert _resolve_path_template(paths, "/orgs/42/users/99") == "/orgs/{org_id}/users/{user_id}"


def test_resolve_path_template_uuid4_value():
    paths = {"/uid/{id}": {}}
    assert (
        _resolve_path_template(paths, "/uid/3f2b4a1c-8e9d-4c7f-b2a1-5e6f7a8b9c0d")
        == "/uid/{id}"
    )


def test_resolve_path_template_raises_on_no_match():
    paths = {"/services/{id}": {}}
    with pytest.raises(SchemaParseError, match="Path '/unknown'"):
        _resolve_path_template(paths, "/unknown")
