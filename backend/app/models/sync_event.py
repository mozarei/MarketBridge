from typing import Any

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin
from app.models.enums import EventStatus


class SyncEvent(TimestampMixin, Base):
    __tablename__ = "sync_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    item_id: Mapped[int | None] = mapped_column(ForeignKey("items.id", ondelete="SET NULL"), index=True)
    channel_listing_id: Mapped[int | None] = mapped_column(
        ForeignKey("channel_listings.id", ondelete="SET NULL"), index=True
    )
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), index=True)
    job_id: Mapped[str | None] = mapped_column(String(128), index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus, name="event_status_enum"), nullable=False)
    message: Mapped[str | None] = mapped_column(String(1024))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    user = relationship("User", back_populates="sync_events")
    item = relationship("Item", back_populates="sync_events")
    channel_listing = relationship("ChannelListing", back_populates="sync_events")
    order = relationship("Order", back_populates="sync_events")
