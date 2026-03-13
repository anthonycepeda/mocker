class SchemaFetchError(Exception):
    """Raised when the OpenAPI schema cannot be fetched from the given URL."""


class SchemaParseError(Exception):
    """Raised when an endpoint or method cannot be found or parsed in the schema."""
