import random
from pathlib import Path

import yaml

_APPS_KEY = "apps"


def load_custom_hints(path: Path) -> dict:
    """Load custom hint value lists from a YAML file.

    Top-level keys (except the reserved `apps` key) are field-name patterns mapped
    to lists of values. The optional `apps` section holds per-app overrides using
    the same pattern → list structure.

    Example file structure::

        status:
          - active
          - inactive

        apps:
          payment-gateway:
            status:
              - processing
              - settled
              - failed

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

    for key, values in data.items():
        if key == _APPS_KEY:
            if not isinstance(values, dict):
                raise ValueError(f"Custom hints: '{_APPS_KEY}' must be a mapping of app names")
            for app_name, app_hints in values.items():
                if not isinstance(app_hints, dict):
                    raise ValueError(
                        f"Custom hints: apps.{app_name} must be a mapping, "
                        f"got: {type(app_hints).__name__}"
                    )
                for field, field_values in app_hints.items():
                    if not isinstance(field_values, list):
                        raise ValueError(
                            f"Custom hints: apps.{app_name}.{field} must be a list, "
                            f"got: {type(field_values).__name__}"
                        )
        else:
            if not isinstance(values, list):
                raise ValueError(
                    f"Custom hints: value for '{key}' must be a list, got: {type(values).__name__}"
                )

    return data


def resolve_hints_for_app(raw_hints: dict, app_name: str | None) -> dict[str, list]:
    """Merge global hints with app-specific overrides for a given app name.

    App-specific hints win over global hints for the same field pattern.
    If `app_name` is None or not present in the `apps` section, only global hints
    are returned.

    Args:
        raw_hints: The dict returned by `load_custom_hints`.
        app_name: The target app name, or None to use global hints only.

    Returns:
        A flat dict of field-pattern → list ready to pass to the generator.
    """
    global_hints = {k: v for k, v in raw_hints.items() if k != _APPS_KEY}
    if not app_name:
        return global_hints
    app_hints = raw_hints.get(_APPS_KEY, {}).get(app_name, {})
    return {**global_hints, **app_hints}


def apply_custom_hint(field_name: str, custom_hints: dict[str, list]) -> tuple[bool, object]:
    """Check if a field name matches a custom hint and return a random value from it.

    Args:
        field_name: The name of the field being generated.
        custom_hints: Flat mapping of pattern → list (already resolved for a specific app).

    Returns:
        A tuple of (matched: bool, value: any).
        If no hint matched, returns (False, None).
    """
    lower = field_name.lower()
    for pattern, values in custom_hints.items():
        if pattern.lower() in lower:
            return True, random.choice(values)
    return False, None
