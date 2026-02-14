from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    items = relationship("Item", back_populates="user")
    connections = relationship("Connection", back_populates="user")
    orders = relationship("Order", back_populates="user")
    sync_events = relationship("SyncEvent", back_populates="user")
