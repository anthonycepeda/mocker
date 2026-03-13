from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"status": "ok"}})

    status: Literal["ok", "ko"] = "ok"


class ProbeResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {}})
