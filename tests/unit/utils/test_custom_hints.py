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
        "sub_name:\n"
        "  generator: slug\n"
        "  min_length: 6\n"
        "  max_length: 20\n"
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


def test_load_global_list_values(hints_file):
    result = load_custom_hints(hints_file)
    assert isinstance(result["status"], list)
    assert isinstance(result["tier"], list)


def test_load_global_generator_spec(hints_file):
    result = load_custom_hints(hints_file)
    assert isinstance(result["sub_name"], dict)
    assert result["sub_name"]["generator"] == "slug"


def test_load_apps_section_is_parsed(hints_file):
    result = load_custom_hints(hints_file)
    assert "apps" in result
    assert "payment-gateway" in result["apps"]


def test_load_raises_on_non_mapping(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("- item1\n- item2\n")
    with pytest.raises(ValueError, match="mapping"):
        load_custom_hints(f)


def test_load_raises_on_invalid_global_value(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("status: active\n")
    with pytest.raises(ValueError, match="list or a generator spec"):
        load_custom_hints(f)


def test_load_raises_on_invalid_app_value(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("apps:\n  payment-gateway:\n    status: active\n")
    with pytest.raises(ValueError, match="list or a generator spec"):
        load_custom_hints(f)


def test_load_raises_on_non_mapping_apps(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("apps:\n  - item\n")
    with pytest.raises(ValueError, match="apps"):
        load_custom_hints(f)


def test_load_accepts_generator_spec_in_apps(tmp_path):
    f = tmp_path / "hints.yaml"
    f.write_text(
        "apps:\n  my-service:\n    sub_name:\n      generator: slug\n      min_length: 6\n"
    )
    result = load_custom_hints(f)
    assert result["apps"]["my-service"]["sub_name"]["generator"] == "slug"


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


def test_apply_list_exact_match(faker):
    hints = {"status": ["active", "inactive"]}
    matched, value = apply_custom_hint("status", hints, faker)
    assert matched
    assert value in ["active", "inactive"]


def test_apply_list_substring_match(faker):
    hints = {"status": ["active", "inactive"]}
    matched, value = apply_custom_hint("payment_status", hints, faker)
    assert matched
    assert value in ["active", "inactive"]


def test_apply_list_case_insensitive(faker):
    hints = {"status": ["active", "inactive"]}
    matched, value = apply_custom_hint("STATUS", hints, faker)
    assert matched
    assert value in ["active", "inactive"]


def test_apply_no_match(faker):
    hints = {"tier": ["gold", "silver"]}
    matched, value = apply_custom_hint("email", hints, faker)
    assert not matched
    assert value is None


def test_apply_generator_spec(faker):
    hints = {"sub_name": {"generator": "slug", "min_length": 6, "max_length": 20}}
    matched, value = apply_custom_hint("sub_name", hints, faker)
    assert matched
    assert isinstance(value, str)
    assert 6 <= len(value) <= 20


def test_apply_generator_spec_substring_match(faker):
    hints = {"hostname": {"generator": "hostname"}}
    matched, value = apply_custom_hint("primary_hostname", hints, faker)
    assert matched
    assert value.startswith("host")


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
