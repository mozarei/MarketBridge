from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin
from app.models.enums import ListingStatus, MarketplaceChannel


class ChannelListing(TimestampMixin, Base):
    __tablename__ = "channel_listings"
    __table_args__ = (UniqueConstraint("item_id", "channel", name="uq_listing_item_channel"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), index=True, nullable=False)
    channel: Mapped[MarketplaceChannel] = mapped_column(Enum(MarketplaceChannel, name="channel_enum"), nullable=False)
    external_listing_id: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status_enum"), default=ListingStatus.DRAFT, nullable=False
    )
    last_error: Mapped[str | None] = mapped_column(String(1024))
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    item = relationship("Item", back_populates="channel_listings")
    sync_events = relationship("SyncEvent", back_populates="channel_listing")
