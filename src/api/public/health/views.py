from fastapi import APIRouter

from src.api.public.health.models import HealthResponse, ProbeResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Basic health check."""
    return HealthResponse()


@router.get("/healthz", response_model=ProbeResponse)
def healthz() -> ProbeResponse:
    """Kubernetes liveness probe."""
    return ProbeResponse()


@router.get("/ready", response_model=ProbeResponse)
def ready() -> ProbeResponse:
    """Kubernetes readiness probe."""
    return ProbeResponse()
