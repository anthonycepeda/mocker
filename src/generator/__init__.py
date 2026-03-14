from faker import Faker

from src.generator.builder import build_value
from src.parser.models import RouteDefinition


def generate_mock(
    route: RouteDefinition, custom_hints: dict[str, list] | None = None
) -> dict | list:
    """Generate a fake but schema-valid response for the given route.

    Args:
        route: A RouteDefinition with a fully resolved response_schema.
        custom_hints: Optional mapping loaded from a custom hints YAML file.

    Returns:
        A dict or list of fake values matching the response schema structure.
    """
    faker = Faker()
    return build_value(route.response_schema, field_name="", faker=faker, custom_hints=custom_hints)
