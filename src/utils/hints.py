import random
import string

from faker import Faker

_REGIONS = ["EMEA", "AMER", "APAC"]


def _random_ecosystem() -> str:
    length = random.randint(4, 10)
    return "".join(random.choices(string.ascii_uppercase, k=length))


_HINTS: dict[str, callable] = {
    "email": lambda f: f.email(),
    "name": lambda f: f.name(),
    "first_name": lambda f: f.first_name(),
    "last_name": lambda f: f.last_name(),
    "phone": lambda f: f.phone_number(),
    "address": lambda f: f.address(),
    "date": lambda f: f.date(),
    "datetime": lambda f: f.iso8601(),
    "amount": lambda f: float(f.pydecimal(min_value=0, max_value=100000, right_digits=2)),
    "iban": lambda f: f.iban(),
    "currency": lambda f: f.currency_code(),
    "url": lambda f: f.url(),
    "uuid": lambda f: f.uuid4(),
    "id": lambda f: f.uuid4(),
    "description": lambda f: f.sentence(),
    "comment": lambda f: f.sentence(),
    "city": lambda f: f.city(),
    "country": lambda f: f.country_code(),
    "zip": lambda f: f.postcode(),
    "postcode": lambda f: f.postcode(),
    "ecosystem": lambda _: _random_ecosystem(),
    "region": lambda _: random.choice(_REGIONS),
}


def apply_hint(
    field_name: str, faker: Faker, custom_hints: dict[str, list] | None = None
) -> tuple[bool, any]:
    """Check if a field name matches a hint and return a fake value.

    Resolution order:
    1. Custom hints (from config file) — checked first so teams can override built-ins
    2. Built-in semantic hints (Faker-based)

    Matches by checking whether any hint key appears as a substring of the
    field name (case-insensitive). For example, "user_email" matches "email".

    Args:
        field_name: The name of the field being generated.
        faker: A Faker instance to use for generation.
        custom_hints: Optional mapping loaded from a custom hints YAML file.

    Returns:
        A tuple of (matched: bool, value: any).
        If no hint matched, returns (False, None).
    """
    if custom_hints:
        from src.utils.custom_hints import apply_custom_hint

        matched, value = apply_custom_hint(field_name, custom_hints)
        if matched:
            return True, value

    lower = field_name.lower()
    for key, generator in _HINTS.items():
        if key in lower:
            return True, generator(faker)
    return False, None
