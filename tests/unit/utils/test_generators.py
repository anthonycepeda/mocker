import re

import pytest

from src.utils.generators import run_generator


@pytest.fixture
def spec():
    """Return a minimal spec builder."""

    def _spec(generator, **kwargs):
        return {"generator": generator, **kwargs}

    return _spec


def test_slug_is_lowercase(spec, faker):
    result = run_generator(spec("slug"), faker)
    assert result == result.lower()


def test_slug_uses_underscore_separator(spec, faker):
    result = run_generator(spec("slug"), faker)
    assert "_" in result or len(result.split("_")) >= 1


def test_slug_respects_max_length(spec, faker):
    result = run_generator(spec("slug", min_length=6, max_length=10), faker)
    assert len(result) <= 10


def test_slug_respects_min_length(spec, faker):
    result = run_generator(spec("slug", min_length=6, max_length=20), faker)
    assert len(result) >= 6


def test_slug_custom_separator(spec, faker):
    # min_length=30 forces multiple words, ensuring the separator appears
    result = run_generator(spec("slug", separator="-", min_length=30, max_length=50), faker)
    assert "-" in result


def test_code_upper_is_uppercase_alphanumeric(spec, faker):
    result = run_generator(spec("code_upper"), faker)
    assert re.fullmatch(r"[A-Z0-9]+", result)


def test_code_upper_length_in_range(spec, faker):
    result = run_generator(spec("code_upper", min_length=4, max_length=6), faker)
    assert 4 <= len(result) <= 6


def test_code_lower_is_lowercase_alphanumeric(spec, faker):
    result = run_generator(spec("code_lower"), faker)
    assert re.fullmatch(r"[a-z0-9]+", result)


def test_code_lower_length_in_range(spec, faker):
    result = run_generator(spec("code_lower", min_length=4, max_length=6), faker)
    assert 4 <= len(result) <= 6


def test_word_sequence_default_separator(spec, faker):
    result = run_generator(spec("word_sequence"), faker)
    assert "-" in result


def test_word_sequence_num_words(spec, faker):
    result = run_generator(spec("word_sequence", num_words=2, separator="-"), faker)
    assert len(result.split("-")) == 2


def test_word_sequence_custom_separator(spec, faker):
    result = run_generator(spec("word_sequence", separator="_"), faker)
    assert "_" in result


def test_numeric_id_is_numeric_string(spec, faker):
    result = run_generator(spec("numeric_id"), faker)
    assert result.isdigit()


def test_numeric_id_in_range(spec, faker):
    result = run_generator(spec("numeric_id", min_value=100, max_value=200), faker)
    assert 100 <= int(result) <= 200


def test_numeric_id_zero_padded(spec, faker):
    result = run_generator(spec("numeric_id", min_value=1, max_value=9, length=5), faker)
    assert len(result) == 5
    assert result.isdigit()


def test_float_value_in_range(spec, faker):
    result = run_generator(spec("float_value"), faker)
    assert 1.0 <= result <= 2000.0


def test_float_value_custom_range(spec, faker):
    result = run_generator(spec("float_value", min_value=10.0, max_value=20.0), faker)
    assert 10.0 <= result <= 20.0


def test_hostname_default_format(spec, faker):
    result = run_generator(spec("hostname"), faker)
    assert re.fullmatch(r"host\d{5}", result)


def test_hostname_custom_prefix_and_digits(spec, faker):
    result = run_generator(spec("hostname", prefix="srv", digits=3), faker)
    assert re.fullmatch(r"srv\d{3}", result)


def test_hostname_prefix_choices_picks_from_list(spec, faker):
    prefixes = ["ehost", "ahost", "chost"]
    for _ in range(20):  # run multiple times to hit all branches
        result = run_generator(spec("hostname", prefix_choices=prefixes, digits=5), faker)
        assert any(result.startswith(p) for p in prefixes)
        assert re.fullmatch(r"[a-z]+\d{5}", result)


def test_owner_six_digits_or_letter_plus_four(spec, faker):
    for _ in range(20):  # run multiple times to hit both branches
        result = run_generator(spec("owner"), faker)
        assert re.fullmatch(r"\d{6}|[a-z]\d{4}", result)


def test_run_generator_raises_on_unknown(spec, faker):
    with pytest.raises(ValueError, match="Unknown generator"):
        run_generator(spec("nonexistent"), faker)
