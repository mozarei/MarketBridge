from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ItemStatus, MarketplaceChannel


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price_cents: int = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    quantity: int = Field(default=1, ge=0)


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price_cents: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    quantity: int | None = Field(default=None, ge=0)
    status: ItemStatus | None = None


class ItemOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    price_cents: int
    currency: str
    quantity: int
    status: ItemStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PublishRequest(BaseModel):
    channel: MarketplaceChannel


class PublishResponse(BaseModel):
    job_id: str
    item_id: int
    channel: MarketplaceChannel
