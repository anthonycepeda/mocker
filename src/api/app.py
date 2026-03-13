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

    app.include_router(public_router)

    return app
