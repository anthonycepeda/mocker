from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from src.api.public.mock.crud import build_mock
from src.api.public.mock.models import MockRequest
from src.utils.exceptions import SchemaFetchError, SchemaParseError

router = APIRouter(tags=["Transparent"])


@router.api_route(
    "/{app_name}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
def transparent_mock(app_name: str, path: str, request: Request) -> JSONResponse:
    """Mock any registered service by replacing the base URL with Mocker's base URL.

    The first path segment is treated as the app name (looked up in APP_REGISTRY).
    The remaining path is used as the endpoint. The HTTP method is inferred from
    the incoming request.

    Example: GET /myservice/users/abc-123 mocks GET /users/abc-123 on myservice.
    """
    mock_request = MockRequest(
        app_name=app_name,
        endpoint=f"/{path}",
        method=request.method,
    )
    try:
        result = build_mock(mock_request)
    except SchemaFetchError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except SchemaParseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return JSONResponse(content=result.data, status_code=result.status_code)
