"""Mapping of well-known internal app names to their OpenAPI schema URLs.

Replace these entries with your own services before deploying.
"""

APP_REGISTRY: dict[str, str] = {
    "service-registry": "http://service-registry/openapi.json",
    "payment-gateway": "http://payment-gateway/openapi.json",
    "order-service": "http://order-service/openapi.json",
    "analytics-service": "http://analytics-service/openapi.json",
    "catalog-service": "http://catalog-service/openapi.json",
    "billing-service": "http://billing-service/openapi.json",
}
