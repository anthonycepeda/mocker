from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI

from src.api.public import router as public_router
from src.config import Settings


def create_app(settings: Settings) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        settings: Application settings instance.

    Returns:
        A configured FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        debug=settings.debug,
        docs_url="/",
    )

    app.add_middleware(
        CorrelationIdMiddleware,
        header_name="X-Request-ID",
        update_request_header=True,
        generator=lambda: uuid4().hex[:10],
        validator=is_valid_uuid4,
        transformer=lambda a: a,
    )

    app.include_router(public_router)

    return app
