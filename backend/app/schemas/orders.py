from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.enums import MarketplaceChannel, OrderStatus


class OrderOut(BaseModel):
    id: int
    user_id: int
    item_id: int | None
    channel: MarketplaceChannel
    external_order_id: str
    status: OrderStatus
    total_cents: int
    currency: str
    buyer_name: str | None
    ordered_at: datetime | None
    raw_payload: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
