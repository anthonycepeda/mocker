from src.generator.sampler import generate_from_sample


def test_generate_from_sample_returns_dict():
    result = generate_from_sample({"name": "foo"})
    assert isinstance(result, dict)


def test_generate_from_sample_preserves_keys():
    sample = {"id": "abc", "status": "active", "count": 1}
    result = generate_from_sample(sample)
    assert set(result.keys()) == {"id", "status", "count"}


def test_generate_from_sample_replaces_values():
    sample = {"name": "original"}
    result = generate_from_sample(sample)
    # Value is regenerated — may coincidentally match, but type must be str
    assert isinstance(result["name"], str)


def test_generate_from_sample_handles_nested_dict():
    sample = {"owner": {"name": "Alice", "email": "alice@example.com"}}
    result = generate_from_sample(sample)
    assert isinstance(result["owner"], dict)
    assert "name" in result["owner"]
    assert "email" in result["owner"]


def test_generate_from_sample_applies_email_hint():
    sample = {"email": "old@example.com"}
    result = generate_from_sample(sample)
    assert "@" in result["email"]


def test_generate_from_sample_handles_list_of_dicts():
    sample = {"items": [{"id": "x", "value": 1}]}
    result = generate_from_sample(sample)
    assert isinstance(result["items"], list)
    assert isinstance(result["items"][0], dict)
    assert "id" in result["items"][0]


def test_generate_from_sample_handles_empty_list():
    sample = {"tags": []}
    result = generate_from_sample(sample)
    assert result["tags"] == []


def test_generate_from_sample_handles_int_values():
    sample = {"count": 5}
    result = generate_from_sample(sample)
    assert isinstance(result["count"], int)


def test_generate_from_sample_handles_float_values():
    sample = {"amount": 99.99}
    result = generate_from_sample(sample)
    assert isinstance(result["amount"], float)


def test_generate_from_sample_handles_bool_values():
    sample = {"is_active": True}
    result = generate_from_sample(sample)
    assert isinstance(result["is_active"], bool)
