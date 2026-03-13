from src.parser.resolver import resolve_refs


def test_resolves_top_level_ref(simple_schema):
    resolved = resolve_refs(simple_schema)
    account = resolved["paths"]["/services/{id}"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert account["type"] == "object"
    assert "id" in account["properties"]


def test_resolves_nested_ref(simple_schema):
    resolved = resolve_refs(simple_schema)
    account = resolved["paths"]["/services/{id}"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    owner = account["properties"]["owner"]
    assert owner["type"] == "object"
    assert "name" in owner["properties"]
    assert "email" in owner["properties"]


def test_does_not_mutate_original(simple_schema):
    original_path_schema = simple_schema["paths"]["/services/{id}"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    resolve_refs(simple_schema)
    assert "$ref" in original_path_schema


def test_circular_ref_returns_empty():
    schema = {
        "paths": {},
        "components": {
            "schemas": {
                "Node": {
                    "type": "object",
                    "properties": {"child": {"$ref": "#/components/schemas/Node"}},
                }
            }
        },
    }
    resolved = resolve_refs(schema)
    node = resolved["components"]["schemas"]["Node"]
    # Resolver expands one level before detecting the cycle — the second child is {}
    assert node["properties"]["child"]["properties"]["child"] == {}
