from fastapi import APIRouter

from src.api.public.mock.views import router as mock_router

router = APIRouter()
router.include_router(mock_router, prefix="/mock")
