from fastapi import APIRouter

from src.api.public.health.views import router as health_router
from src.api.public.mock.views import router as mock_router

router = APIRouter()
router.include_router(health_router, tags=["Health"])
router.include_router(mock_router, prefix="/mock", tags=["Mock"])
