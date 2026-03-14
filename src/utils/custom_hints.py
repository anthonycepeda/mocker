import random
from pathlib import Path

import yaml


def load_custom_hints(path: Path) -> dict[str, list]:
    """Load custom hint value lists from a YAML file.

    The file must be a YAML mapping of field-name patterns to lists of values.
    Each key is matched as a substring of the field name (case-insensitive),
    same behaviour as the built-in semantic hints.

    Args:
        path: Path to the YAML file.

    Returns:
        A dict mapping pattern strings to lists of allowed values.

    Raises:
        ValueError: If the file is not a valid YAML mapping or any value is not a list.
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Custom hints file must be a YAML mapping, got: {type(data).__name__}")

    for key, values in data.items():
        if not isinstance(values, list):
            raise ValueError(
                f"Custom hints: value for '{key}' must be a list, got: {type(values).__name__}"
            )

    return data


def apply_custom_hint(field_name: str, custom_hints: dict[str, list]) -> tuple[bool, object]:
    """Check if a field name matches a custom hint and return a random value from it.

    Args:
        field_name: The name of the field being generated.
        custom_hints: Mapping loaded from the custom hints YAML file.

    Returns:
        A tuple of (matched: bool, value: any).
        If no hint matched, returns (False, None).
    """
    lower = field_name.lower()
    for pattern, values in custom_hints.items():
        if pattern.lower() in lower:
            return True, random.choice(values)
    return False, None
