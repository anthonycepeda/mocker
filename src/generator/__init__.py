from faker import Faker

from src.generator.builder import build_value
from src.parser.models import RouteDefinition


def generate_mock(route: RouteDefinition) -> dict:
    """Generate a fake but schema-valid response dict for the given route.

    Args:
        route: A RouteDefinition with a fully resolved response_schema.

    Returns:
        A dict of fake values matching the response schema structure.
    """
    faker = Faker()
    return build_value(route.response_schema, field_name="", faker=faker)
