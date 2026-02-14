from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.enums import EventStatus


class SyncEventOut(BaseModel):
    id: int
    user_id: int | None
    item_id: int | None
    channel_listing_id: int | None
    order_id: int | None
    job_id: str | None
    event_type: str
    status: EventStatus
    message: str | None
    payload: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True
