from faker import Faker

from src.utils.hints import apply_hint


def generate_from_sample(sample: dict, custom_hints: dict[str, list] | None = None) -> dict:
    """Regenerate fake data from a caller-provided response sample.

    Walks the sample recursively, preserving its shape. For each leaf value,
    applies semantic hints by field name first, then falls back to type-based
    generation. The sample itself is never returned — all values are replaced.

    Args:
        sample: A real or representative response dict to use as a shape template.
        custom_hints: Optional mapping loaded from a custom hints YAML file.

    Returns:
        A new dict with the same structure but freshly generated fake values.
    """
    faker = Faker()
    return _regenerate(sample, field_name="", faker=faker, custom_hints=custom_hints)


def _regenerate(
    value: object, field_name: str, faker: Faker, custom_hints: dict[str, list] | None = None
) -> object:
    """Recursively regenerate a value based on its type and field name."""
    if isinstance(value, dict):
        return {
            k: _regenerate(v, field_name=k, faker=faker, custom_hints=custom_hints)
            for k, v in value.items()
        }

    if isinstance(value, list):
        if not value:
            return []
        return [
            _regenerate(item, field_name=field_name, faker=faker, custom_hints=custom_hints)
            for item in value
        ]

    matched, hint_value = apply_hint(field_name, faker, custom_hints)
    if matched:
        return hint_value

    if isinstance(value, bool):
        return faker.boolean()

    if isinstance(value, int):
        return faker.random_int(min=1, max=9999)

    if isinstance(value, float):
        return round(faker.pyfloat(min_value=0, max_value=10000), 2)

    if isinstance(value, str):
        return faker.word()

    return value
