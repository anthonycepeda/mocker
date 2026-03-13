import uvicorn

from src.api.app import create_app
from src.config import get_settings

settings = get_settings()
app = create_app(settings)

if __name__ == "__main__":
    uvicorn.run("asgi:app", host="0.0.0.0", port=8080, reload=True)
