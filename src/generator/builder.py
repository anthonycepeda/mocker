import random

from faker import Faker

from src.utils.hints import apply_hint


def build_value(schema: dict, field_name: str, faker: Faker) -> any:
    """Recursively build a fake value for a given JSON Schema node.

    Resolution order:
    1. Semantic hint (field name match)
    2. Enum
    3. anyOf (pick first non-null branch)
    4. Type-based generation

    Args:
        schema: A fully resolved JSON Schema dict for this field.
        field_name: The name of the field, used for semantic hint matching.
        faker: A Faker instance for generating values.

    Returns:
        A fake value matching the schema's type and constraints.
    """
    matched, hint_value = apply_hint(field_name, faker)
    if matched:
        return hint_value

    if "enum" in schema:
        return random.choice(schema["enum"])

    if "anyOf" in schema:
        non_null = [s for s in schema["anyOf"] if s.get("type") != "null"]
        if non_null:
            return build_value(non_null[0], field_name, faker)
        return None

    schema_type = schema.get("type")

    if schema_type == "object":
        return _build_object(schema, faker)

    if schema_type == "array":
        return _build_array(schema, field_name, faker)

    if schema_type == "string":
        return faker.word()

    if schema_type == "integer":
        return faker.random_int(min=1, max=9999)

    if schema_type == "number":
        return round(faker.pyfloat(min_value=0, max_value=10000), 2)

    if schema_type == "boolean":
        return faker.boolean()

    return None


def _build_object(schema: dict, faker: Faker) -> dict:
    """Build a fake dict from an object schema's properties."""
    properties = schema.get("properties", {})
    return {
        field: build_value(field_schema, field, faker) for field, field_schema in properties.items()
    }


def _build_array(schema: dict, field_name: str, faker: Faker) -> list:
    """Build a fake list from an array schema's items definition."""
    items_schema = schema.get("items", {})
    count = random.randint(1, 3)
    return [build_value(items_schema, field_name, faker) for _ in range(count)]
