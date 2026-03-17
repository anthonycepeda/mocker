from faker import Faker

from src.generator.builder import build_value
from src.parser.models import RouteDefinition


def generate_mock(
    route: RouteDefinition,
    custom_hints: dict[str, list] | None = None,
    overrides: dict | None = None,
) -> dict | list:
    """Generate a fake but schema-valid response for the given route.

    If ``overrides`` is provided and the response is a dict, any key in ``overrides``
    that matches a top-level field in the generated response is replaced with the
    provided value. Unknown keys are silently ignored.

    Args:
        route: A RouteDefinition with a fully resolved response_schema.
        custom_hints: Optional mapping loaded from a custom hints YAML file.
        overrides: Optional dict of input values to echo back in the response
            (e.g. body fields, query params) for deterministic test assertions.

    Returns:
        A dict or list of fake values matching the response schema structure.
    """
    faker = Faker()
    result = build_value(
        route.response_schema, field_name="", faker=faker, custom_hints=custom_hints
    )
    if overrides and isinstance(result, dict):
        result.update({k: v for k, v in overrides.items() if k in result})
    return result
