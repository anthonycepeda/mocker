from src.generator.generator import generate_mock
from src.parser.models import RouteDefinition


def test_generate_mock_returns_dict(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/accounts/{id}", "GET")
    result = generate_mock(route)
    assert isinstance(result, dict)


def test_generate_mock_contains_expected_keys(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/accounts/{id}", "GET")
    result = generate_mock(route)
    assert "id" in result
    assert "balance" in result
    assert "owner" in result


def test_generate_mock_nested_object(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/accounts/{id}", "GET")
    result = generate_mock(route)
    assert isinstance(result["owner"], dict)
    assert "name" in result["owner"]
    assert "email" in result["owner"]


def test_generate_mock_email_hint_applied(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/accounts/{id}", "GET")
    result = generate_mock(route)
    assert "@" in result["owner"]["email"]


def test_generate_mock_produces_different_results_each_call(simple_schema):
    from src.parser.parser import parse_route

    route = parse_route(simple_schema, "/accounts/{id}", "GET")
    result_1 = generate_mock(route)
    result_2 = generate_mock(route)
    # Not guaranteed but extremely unlikely to be identical
    assert result_1 != result_2


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
