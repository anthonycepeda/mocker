import random
from pathlib import Path

import yaml
from faker import Faker

_APPS_KEY = "apps"


def _validate_hint_value(key: str, value: object) -> None:
    """Raise ValueError if value is not a valid hint spec (list or generator dict)."""
    if isinstance(value, list):
        return
    if isinstance(value, dict) and "generator" in value:
        return
    raise ValueError(
        f"Custom hints: value for '{key}' must be a list or a generator spec "
        f"(dict with a 'generator' key), got: {type(value).__name__}"
    )


def load_custom_hints(path: Path) -> dict:
    """Load custom hints from a YAML file.

    Each top-level key (except the reserved `apps` key) is a field-name pattern
    mapped to either a list of values or a generator spec dict.

    Generator spec example::

        sub_name:
          generator: slug
          min_length: 6
          max_length: 20

    The optional `apps` section holds per-app overrides using the same
    pattern → list/spec structure.

    Args:
        path: Path to the YAML file.

    Returns:
        The raw parsed dict, including any `apps` section.

    Raises:
        ValueError: If the file structure is invalid.
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Custom hints file must be a YAML mapping, got: {type(data).__name__}")

    for key, value in data.items():
        if key == _APPS_KEY:
            if not isinstance(value, dict):
                raise ValueError(f"Custom hints: '{_APPS_KEY}' must be a mapping of app names")
            for app_name, app_hints in value.items():
                if not isinstance(app_hints, dict):
                    raise ValueError(
                        f"Custom hints: apps.{app_name} must be a mapping, "
                        f"got: {type(app_hints).__name__}"
                    )
                for field, field_value in app_hints.items():
                    _validate_hint_value(f"apps.{app_name}.{field}", field_value)
        else:
            _validate_hint_value(key, value)

    return data


def resolve_hints_for_app(raw_hints: dict, app_name: str | None) -> dict:
    """Merge global hints with app-specific overrides for a given app name.

    App-specific hints win over global hints for the same field pattern.
    If `app_name` is None or not present in the `apps` section, only global hints
    are returned.

    Args:
        raw_hints: The dict returned by `load_custom_hints`.
        app_name: The target app name, or None to use global hints only.

    Returns:
        A flat dict of field-pattern → list or generator spec.
    """
    global_hints = {k: v for k, v in raw_hints.items() if k != _APPS_KEY}
    if not app_name:
        return global_hints
    app_hints = raw_hints.get(_APPS_KEY, {}).get(app_name, {})
    return {**global_hints, **app_hints}


def apply_custom_hint(field_name: str, custom_hints: dict, faker: Faker) -> tuple[bool, object]:
    """Check if a field name matches a custom hint and return a generated value.

    Supports two hint styles:
    - List: picks a random item from the list.
    - Generator spec: runs the named generator with the given constraints.

    Args:
        field_name: The name of the field being generated.
        custom_hints: Flat mapping of pattern → list or generator spec.
        faker: A Faker instance for generators that need word generation.

    Returns:
        A tuple of (matched: bool, value: any).
        If no hint matched, returns (False, None).
    """
    from src.utils.generators import run_generator

    lower = field_name.lower()
    for pattern, spec in custom_hints.items():
        if pattern.lower() in lower:
            if isinstance(spec, list):
                return True, random.choice(spec)
            return True, run_generator(spec, faker)
    return False, None
