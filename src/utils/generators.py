import random
import string

from faker import Faker


def generate_slug(spec: dict, faker: Faker) -> str:
    """Lowercase words joined by underscores (or custom separator).

    Spec keys: min_length (default 6), max_length (default 20), separator (default '_').
    """
    min_len = spec.get("min_length", 6)
    max_len = spec.get("max_length", 20)
    sep = spec.get("separator", "_")
    parts = []
    while True:
        parts.append(faker.word().lower())
        result = sep.join(parts)
        if len(result) >= min_len:
            break
    return result[:max_len]


def generate_code_upper(spec: dict, faker: Faker) -> str:
    """Short uppercase alphanumeric code — no spaces or underscores.

    Spec keys: min_length (default 6), max_length (default 8).
    """
    min_len = spec.get("min_length", 6)
    max_len = spec.get("max_length", 8)
    length = random.randint(min_len, max_len)
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def generate_code_lower(spec: dict, faker: Faker) -> str:
    """Short lowercase alphanumeric code — no spaces or underscores.

    Spec keys: min_length (default 6), max_length (default 8).
    """
    min_len = spec.get("min_length", 6)
    max_len = spec.get("max_length", 8)
    length = random.randint(min_len, max_len)
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


def generate_word_sequence(spec: dict, faker: Faker) -> str:
    """Readable sequence of random words joined by a separator.

    Spec keys: num_words (default 3), separator (default '-').
    """
    num_words = spec.get("num_words", 3)
    sep = spec.get("separator", "-")
    return sep.join(faker.word().lower() for _ in range(num_words))


def generate_numeric_id(spec: dict, faker: Faker) -> str:
    """Random integer as a string, optionally zero-padded.

    Spec keys: min_value (default 1), max_value (default 99999), length (zero-pad to N digits).
    """
    min_value = spec.get("min_value", 1)
    max_value = spec.get("max_value", 99999)
    length = spec.get("length", None)
    value = random.randint(min_value, max_value)
    return str(value).zfill(length) if length else str(value)


def generate_float_value(spec: dict, faker: Faker) -> float:
    """Random float in a range.

    Spec keys: min_value (default 1.0), max_value (default 2000.0).
    """
    min_value = spec.get("min_value", 1.0)
    max_value = spec.get("max_value", 2000.0)
    return round(random.uniform(min_value, max_value), 2)


def generate_hostname(spec: dict, faker: Faker) -> str:
    """Fixed prefix followed by a zero-padded numeric suffix.

    Spec keys: prefix (default 'host'), digits (default 5).
    Example: host00042
    """
    prefix = spec.get("prefix", "host")
    digits = spec.get("digits", 5)
    number = random.randint(1, 10**digits - 1)
    return f"{prefix}{str(number).zfill(digits)}"


def generate_owner(spec: dict, faker: Faker) -> str:
    """Owner identifier: either 6 digits or one lowercase letter followed by 4 digits.

    Examples: 123456 | u1234
    No spec keys.
    """
    if random.choice([True, False]):
        return str(random.randint(100000, 999999))
    letter = random.choice(string.ascii_lowercase)
    digits = str(random.randint(1000, 9999))
    return f"{letter}{digits}"


_GENERATORS: dict[str, callable] = {
    "slug": generate_slug,
    "code_upper": generate_code_upper,
    "code_lower": generate_code_lower,
    "word_sequence": generate_word_sequence,
    "numeric_id": generate_numeric_id,
    "float_value": generate_float_value,
    "hostname": generate_hostname,
    "owner": generate_owner,
}


def run_generator(spec: dict, faker: Faker) -> object:
    """Dispatch to the named generator and return the generated value.

    Args:
        spec: A dict containing a 'generator' key and optional constraint keys.
        faker: A Faker instance for word generation.

    Returns:
        The generated value.

    Raises:
        ValueError: If the generator name is not recognised.
    """
    name = spec["generator"]
    fn = _GENERATORS.get(name)
    if fn is None:
        raise ValueError(f"Unknown generator: '{name}'. Available: {sorted(_GENERATORS)}")
    return fn(spec, faker)
