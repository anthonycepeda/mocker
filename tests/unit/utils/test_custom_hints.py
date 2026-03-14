import pytest

from src.utils.custom_hints import apply_custom_hint, load_custom_hints


@pytest.fixture
def hints_file(tmp_path):
    f = tmp_path / "hints.yaml"
    f.write_text("status:\n  - active\n  - inactive\n  - pending\ntier:\n  - gold\n  - silver\n")
    return f


def test_load_returns_dict(hints_file):
    result = load_custom_hints(hints_file)
    assert isinstance(result, dict)


def test_load_values_are_lists(hints_file):
    result = load_custom_hints(hints_file)
    assert isinstance(result["status"], list)
    assert isinstance(result["tier"], list)


def test_load_raises_on_non_mapping(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("- item1\n- item2\n")
    with pytest.raises(ValueError, match="mapping"):
        load_custom_hints(f)


def test_load_raises_on_non_list_value(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text("status: active\n")
    with pytest.raises(ValueError, match="list"):
        load_custom_hints(f)


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
