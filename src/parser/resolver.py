def resolve_refs(schema: dict) -> dict:
    """Resolve all $ref pointers in the schema, returning a fully inlined copy.

    Handles nested and circular references. The original schema is not mutated.

    Args:
        schema: Raw OpenAPI schema dict as returned by fetch_schema.

    Returns:
        A new dict with all $ref pointers replaced by their inline definitions.
    """
    components = schema.get("components", {}).get("schemas", {})
    return _resolve_node(schema, components, visited=frozenset())


def _resolve_node(node: dict | list, components: dict, visited: frozenset) -> dict | list:
    """Recursively resolve $ref pointers within a node."""
    if isinstance(node, list):
        return [_resolve_node(item, components, visited) for item in node]

    if not isinstance(node, dict):
        return node

    if "$ref" in node:
        ref = node["$ref"]
        if ref in visited:
            return {}
        name = ref.split("/")[-1]
        target = components.get(name, {})
        return _resolve_node(target, components, visited | {ref})

    return {key: _resolve_node(value, components, visited) for key, value in node.items()}
