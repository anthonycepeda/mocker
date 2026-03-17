from src.generator import generate_mock
from src.parser.models import RouteDefinition


def test_generate_mock_returns_dict(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route)
    assert isinstance(result, dict)


def test_generate_mock_contains_expected_keys(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route)
    assert "id" in result
    assert "region" in result
    assert "ecosystem" in result
    assert "owner" in result


def test_generate_mock_nested_object(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route)
    assert isinstance(result["owner"], dict)
    assert "name" in result["owner"]
    assert "email" in result["owner"]


def test_generate_mock_email_hint_applied(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route)
    assert "@" in result["owner"]["email"]


def test_generate_mock_region_hint_applied(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route)
    assert result["region"] in ("EMEA", "AMER", "APAC")


def test_generate_mock_ecosystem_hint_applied(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route)
    assert result["ecosystem"].isupper()
    assert 4 <= len(result["ecosystem"]) <= 10


def test_generate_mock_produces_different_results_each_call(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result_1 = generate_mock(route)
    result_2 = generate_mock(route)
    # Not guaranteed but extremely unlikely to be identical
    assert result_1 != result_2


def test_generate_mock_overrides_matching_field(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route, overrides={"region": "EMEA"})
    assert result["region"] == "EMEA"


def test_generate_mock_overrides_ignores_unknown_keys(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route, overrides={"nonexistent_field": "value"})
    assert "nonexistent_field" not in result


def test_generate_mock_overrides_multiple_fields(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/services/{id}", "GET")
    result = generate_mock(route, overrides={"region": "AMER", "ecosystem": "CORE"})
    assert result["region"] == "AMER"
    assert result["ecosystem"] == "CORE"


def test_generate_mock_overrides_skipped_for_list_response():
    route = RouteDefinition(
        path="/items",
        method="get",
        response_schema={"type": "array", "items": {"type": "string"}},
    )
    result = generate_mock(route, overrides={"region": "EMEA"})
    assert isinstance(result, list)


def test_generate_mock_works_with_inline_route_definition():
    route = RouteDefinition(
        path="/items",
        method="get",
        response_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "inactive"]},
                "count": {"type": "integer"},
            },
        },
    )
    result = generate_mock(route)
    assert result["status"] in ["active", "inactive"]
    assert isinstance(result["count"], int)
