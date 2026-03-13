import httpx

from src.utils.exceptions import SchemaFetchError


def fetch_schema(url: str) -> dict:
    """Fetch and return the raw OpenAPI schema from the given URL.

    Raises:
        SchemaFetchError: If the URL is unreachable or returns a non-200 response.
    """
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise SchemaFetchError(
            f"Failed to fetch schema from {url}: HTTP {e.response.status_code}"
        ) from e
    except httpx.RequestError as e:
        raise SchemaFetchError(
            f"Failed to reach {url}: {e}"
        ) from e
