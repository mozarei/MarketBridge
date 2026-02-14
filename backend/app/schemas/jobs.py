from typing import Any

from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    job_id: str
    state: str
    ready: bool
    successful: bool | None
    result: Any = None
    error: str | None = None
