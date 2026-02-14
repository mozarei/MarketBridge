"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-02-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


channel_enum = postgresql.ENUM("EBAY", "ETSY", "POSHMARK", name="channel_enum", create_type=False)
connection_status_enum = postgresql.ENUM(
    "ACTIVE", "EXPIRED", "REVOKED", name="connection_status_enum", create_type=False
)
item_status_enum = postgresql.ENUM("DRAFT", "ACTIVE", "ARCHIVED", name="item_status_enum", create_type=False)
listing_status_enum = postgresql.ENUM(
    "DRAFT",
    "PUBLISH_QUEUED",
    "LIVE",
    "DELIST_QUEUED",
    "DELISTED",
    "ERROR",
    name="listing_status_enum",
    create_type=False,
)
order_status_enum = postgresql.ENUM("NEW", "PAID", "SHIPPED", "CANCELED", name="order_status_enum", create_type=False)
event_status_enum = postgresql.ENUM("STARTED", "SUCCEEDED", "FAILED", name="event_status_enum", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    channel_enum.create(bind, checkfirst=True)
    connection_status_enum.create(bind, checkfirst=True)
    item_status_enum.create(bind, checkfirst=True)
    listing_status_enum.create(bind, checkfirst=True)
    order_status_enum.create(bind, checkfirst=True)
    event_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel", channel_enum, nullable=False),
        sa.Column("access_token", sa.String(length=1024), nullable=False),
        sa.Column("refresh_token", sa.String(length=1024), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", connection_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "channel", name="uq_connection_user_channel"),
    )

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", item_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_items_user_id"), "items", ["user_id"], unique=False)

    op.create_table(
        "channel_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("channel", channel_enum, nullable=False),
        sa.Column("external_listing_id", sa.String(length=255), nullable=True),
        sa.Column("status", listing_status_enum, nullable=False),
        sa.Column("last_error", sa.String(length=1024), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "channel", name="uq_listing_item_channel"),
    )
    op.create_index(op.f("ix_channel_listings_external_listing_id"), "channel_listings", ["external_listing_id"], unique=False)
    op.create_index(op.f("ix_channel_listings_item_id"), "channel_listings", ["item_id"], unique=False)
    op.create_index(op.f("ix_channel_listings_user_id"), "channel_listings", ["user_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("channel", channel_enum, nullable=False),
        sa.Column("external_order_id", sa.String(length=255), nullable=False),
        sa.Column("status", order_status_enum, nullable=False),
        sa.Column("total_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("buyer_name", sa.String(length=255), nullable=True),
        sa.Column("ordered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("channel", "external_order_id", name="uq_order_channel_external_id"),
    )
    op.create_index(op.f("ix_orders_item_id"), "orders", ["item_id"], unique=False)
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"], unique=False)

    op.create_table(
        "sync_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("channel_listing_id", sa.Integer(), nullable=True),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.String(length=128), nullable=True),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("status", event_status_enum, nullable=False),
        sa.Column("message", sa.String(length=1024), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["channel_listing_id"], ["channel_listings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sync_events_channel_listing_id"), "sync_events", ["channel_listing_id"], unique=False)
    op.create_index(op.f("ix_sync_events_item_id"), "sync_events", ["item_id"], unique=False)
    op.create_index(op.f("ix_sync_events_job_id"), "sync_events", ["job_id"], unique=False)
    op.create_index(op.f("ix_sync_events_order_id"), "sync_events", ["order_id"], unique=False)
    op.create_index(op.f("ix_sync_events_user_id"), "sync_events", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sync_events_user_id"), table_name="sync_events")
    op.drop_index(op.f("ix_sync_events_order_id"), table_name="sync_events")
    op.drop_index(op.f("ix_sync_events_job_id"), table_name="sync_events")
    op.drop_index(op.f("ix_sync_events_item_id"), table_name="sync_events")
    op.drop_index(op.f("ix_sync_events_channel_listing_id"), table_name="sync_events")
    op.drop_table("sync_events")

    op.drop_index(op.f("ix_orders_user_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_item_id"), table_name="orders")
    op.drop_table("orders")

    op.drop_index(op.f("ix_channel_listings_user_id"), table_name="channel_listings")
    op.drop_index(op.f("ix_channel_listings_item_id"), table_name="channel_listings")
    op.drop_index(op.f("ix_channel_listings_external_listing_id"), table_name="channel_listings")
    op.drop_table("channel_listings")

    op.drop_index(op.f("ix_items_user_id"), table_name="items")
    op.drop_table("items")

    op.drop_table("connections")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    event_status_enum.drop(bind, checkfirst=True)
    order_status_enum.drop(bind, checkfirst=True)
    listing_status_enum.drop(bind, checkfirst=True)
    item_status_enum.drop(bind, checkfirst=True)
    connection_status_enum.drop(bind, checkfirst=True)
    channel_enum.drop(bind, checkfirst=True)
