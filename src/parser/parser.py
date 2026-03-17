from src.parser.models import RouteDefinition
from src.parser.resolver import resolve_refs
from src.utils.exceptions import SchemaParseError


def parse_route(schema: dict, path: str, method: str) -> RouteDefinition:
    """Extract and return a fully resolved RouteDefinition for the given path and method.

    Args:
        schema: Raw OpenAPI schema dict as returned by fetch_schema.
        path: The endpoint path, e.g. "/accounts/{id}".
        method: The HTTP method, e.g. "GET". Case-insensitive.

    Returns:
        A RouteDefinition with a fully resolved response_schema and the actual status code
        from the schema (first 2xx response found).

    Raises:
        SchemaParseError: If the path or method is not found, or has no 2xx response schema.
    """
    resolved = resolve_refs(schema)
    method_lower = method.lower()

    paths = resolved.get("paths", {})
    if path not in paths:
        raise SchemaParseError(f"Path '{path}' not found in schema")

    route = paths[path]
    if method_lower not in route:
        raise SchemaParseError(f"Method '{method.upper()}' not found for path '{path}'")

    responses = route[method_lower]["responses"]
    status_code = None
    response_schema = None
    for code in sorted(str(k) for k in responses.keys()):
        if code.startswith("2"):
            try:
                response_schema = responses[code]["content"]["application/json"]["schema"]
                status_code = int(code)
                break
            except KeyError:
                continue

    if response_schema is None:
        raise SchemaParseError(
            f"No 2xx JSON response schema found for {method.upper()} {path}"
        )

    return RouteDefinition(
        path=path, method=method_lower, response_schema=response_schema, status_code=status_code
    )
