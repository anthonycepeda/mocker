import pytest
from faker import Faker

from src.generator.builder import build_value


@pytest.fixture
def faker():
    return Faker()


def test_builds_string(faker):
    result = build_value({"type": "string"}, "word", faker)
    assert isinstance(result, str)


def test_builds_integer(faker):
    result = build_value({"type": "integer"}, "count", faker)
    assert isinstance(result, int)


def test_builds_number(faker):
    result = build_value({"type": "number"}, "ratio", faker)
    assert isinstance(result, float)


def test_builds_boolean(faker):
    result = build_value({"type": "boolean"}, "active", faker)
    assert isinstance(result, bool)


def test_builds_object(faker):
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
    }
    result = build_value(schema, "", faker)
    assert isinstance(result, dict)
    assert "name" in result
    assert "age" in result
    assert isinstance(result["name"], str)
    assert isinstance(result["age"], int)


def test_builds_array(faker):
    schema = {"type": "array", "items": {"type": "string"}}
    result = build_value(schema, "tags", faker)
    assert isinstance(result, list)
    assert 1 <= len(result) <= 3
    assert all(isinstance(item, str) for item in result)


def test_enum_returns_valid_choice(faker):
    schema = {"type": "string", "enum": ["active", "pending", "closed"]}
    result = build_value(schema, "status", faker)
    assert result in ["active", "pending", "closed"]


def test_any_of_picks_non_null_branch(faker):
    schema = {"anyOf": [{"type": "string"}, {"type": "null"}]}
    result = build_value(schema, "label", faker)
    assert isinstance(result, str)


def test_unknown_type_returns_none(faker):
    result = build_value({"type": "unknown"}, "field", faker)
    assert result is None


def test_hint_fires_for_email_field(faker):
    result = build_value({"type": "string"}, "email", faker)
    assert "@" in result


def test_hint_fires_on_substring_match(faker):
    result = build_value({"type": "string"}, "user_email", faker)
    assert "@" in result


def test_hint_takes_priority_over_type(faker):
    result = build_value({"type": "string"}, "contact_email", faker)
    assert "@" in result


def test_region_hint(faker):
    result = build_value({"type": "string"}, "region", faker)
    assert result in ["EMEA", "AMER", "APAC"]


def test_ecosystem_hint(faker):
    result = build_value({"type": "string"}, "ecosystem", faker)
    assert isinstance(result, str)
    assert result.isupper()
    assert 4 <= len(result) <= 10
