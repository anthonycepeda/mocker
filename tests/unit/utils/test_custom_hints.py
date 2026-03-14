import pytest

from src.utils.custom_hints import apply_custom_hint, load_custom_hints, resolve_hints_for_app


@pytest.fixture
def hints_file(tmp_path):
    f = tmp_path / "hints.yaml"
    f.write_text(
        "status:\n"
        "  - active\n"
        "  - inactive\n"
        "tier:\n"
        "  - gold\n"
        "  - silver\n"
        "apps:\n"
        "  payment-gateway:\n"
        "    status:\n"
        "      - processing\n"
        "      - settled\n"
    )
    return f


# --- load_custom_hints ---


def test_load_returns_dict(hints_file):
    result = load_custom_hints(hints_file)
    assert isinstance(result, dict)


def test_load_global_values_are_lists(hints_file):
    result = load_custom_hints(hints_file)
    assert isinstance(result["status"], list)
    assert isinstance(result["tier"], list)


def test_load_apps_section_is_parsed(hints_file):
    result = load_custom_hints(hints_file)
    assert "apps" in result
    assert "payment-gateway" in result["apps"]


def test_load_raises_on_non_mapping(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("- item1\n- item2\n")
    with pytest.raises(ValueError, match="mapping"):
        load_custom_hints(f)


def test_load_raises_on_non_list_global_value(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("status: active\n")
    with pytest.raises(ValueError, match="list"):
        load_custom_hints(f)


def test_load_raises_on_non_list_app_value(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("apps:\n  payment-gateway:\n    status: active\n")
    with pytest.raises(ValueError, match="list"):
        load_custom_hints(f)


def test_load_raises_on_non_mapping_apps(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("apps:\n  - item\n")
    with pytest.raises(ValueError, match="apps"):
        load_custom_hints(f)


# --- resolve_hints_for_app ---


def test_resolve_no_app_returns_global_only(hints_file):
    raw = load_custom_hints(hints_file)
    result = resolve_hints_for_app(raw, app_name=None)
    assert "status" in result
    assert "apps" not in result


def test_resolve_app_overrides_global(hints_file):
    raw = load_custom_hints(hints_file)
    result = resolve_hints_for_app(raw, app_name="payment-gateway")
    assert result["status"] == ["processing", "settled"]


def test_resolve_app_inherits_non_overridden_globals(hints_file):
    raw = load_custom_hints(hints_file)
    result = resolve_hints_for_app(raw, app_name="payment-gateway")
    assert result["tier"] == ["gold", "silver"]


def test_resolve_unknown_app_returns_global_only(hints_file):
    raw = load_custom_hints(hints_file)
    result = resolve_hints_for_app(raw, app_name="unknown-service")
    assert result["status"] == ["active", "inactive"]


def test_resolve_apps_key_not_in_result(hints_file):
    raw = load_custom_hints(hints_file)
    result = resolve_hints_for_app(raw, app_name="payment-gateway")
    assert "apps" not in result


# --- apply_custom_hint ---


def test_apply_exact_match():
    hints = {"status": ["active", "inactive"]}
    matched, value = apply_custom_hint("status", hints)
    assert matched
    assert value in ["active", "inactive"]


def test_apply_substring_match():
    hints = {"status": ["active", "inactive"]}
    matched, value = apply_custom_hint("payment_status", hints)
    assert matched
    assert value in ["active", "inactive"]


def test_apply_case_insensitive():
    hints = {"status": ["active", "inactive"]}
    matched, value = apply_custom_hint("STATUS", hints)
    assert matched
    assert value in ["active", "inactive"]


def test_apply_no_match():
    hints = {"tier": ["gold", "silver"]}
    matched, value = apply_custom_hint("email", hints)
    assert not matched
    assert value is None


def test_custom_hint_overrides_faker_hint(faker):
    """Custom hint for 'email' must win over the built-in faker email hint."""
    from src.utils.hints import apply_hint

    custom = {"email": ["fake@corp.internal"]}
    matched, value = apply_hint("email", faker, custom_hints=custom)
    assert matched
    assert value == "fake@corp.internal"


def test_faker_hint_fires_when_no_custom_hint(faker):
    from src.utils.hints import apply_hint

    matched, value = apply_hint("email", faker, custom_hints={})
    assert matched
    assert "@" in value
