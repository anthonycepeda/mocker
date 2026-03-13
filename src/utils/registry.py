"""Mapping of well-known internal app names to their OpenAPI schema URLs."""

APP_REGISTRY: dict[str, str] = {
    "service-registry": "http://service-registry/openapi.json",
    "trading-gateway": "http://trading-gateway/openapi.json",
    "order-router": "http://order-router/openapi.json",
    "risk-engine": "http://risk-engine/openapi.json",
    "market-data": "http://market-data/openapi.json",
    "settlement-service": "http://settlement-service/openapi.json",
}
