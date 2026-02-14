from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin
from app.models.enums import ConnectionStatus, MarketplaceChannel


class Connection(TimestampMixin, Base):
    __tablename__ = "connections"
    __table_args__ = (UniqueConstraint("user_id", "channel", name="uq_connection_user_channel"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[MarketplaceChannel] = mapped_column(Enum(MarketplaceChannel, name="channel_enum"), nullable=False)
    access_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String(1024))
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[ConnectionStatus] = mapped_column(
        Enum(ConnectionStatus, name="connection_status_enum"), default=ConnectionStatus.ACTIVE, nullable=False
    )

    user = relationship("User", back_populates="connections")
