from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.channel_listing import ChannelListing
from app.models.enums import EventStatus, ListingStatus, MarketplaceChannel
from app.models.item import Item
from app.models.sync_event import SyncEvent
from app.tasks.celery_app import celery_app


def _log_sync_event(
    *,
    user_id: int | None,
    item_id: int | None,
    channel_listing_id: int | None,
    order_id: int | None,
    job_id: str | None,
    event_type: str,
    status: EventStatus,
    message: str,
    payload: dict | None = None,
) -> None:
    with SessionLocal() as db:
        db.add(
            SyncEvent(
                user_id=user_id,
                item_id=item_id,
                channel_listing_id=channel_listing_id,
                order_id=order_id,
                job_id=job_id,
                event_type=event_type,
                status=status,
                message=message,
                payload=payload,
            )
        )
        db.commit()


@celery_app.task(bind=True, name="jobs.publish_item")
def publish_item(self, item_id: int, channel: str, user_id: int) -> dict:
    job_id = self.request.id
    parsed_channel: MarketplaceChannel | None = None
    _log_sync_event(
        user_id=user_id,
        item_id=item_id,
        channel_listing_id=None,
        order_id=None,
        job_id=job_id,
        event_type="publish_started",
        status=EventStatus.STARTED,
        message=f"Publish job started for item {item_id} on {channel}",
        payload={"channel": channel},
    )

    try:
        marketplace = MarketplaceChannel(channel)
        parsed_channel = marketplace
        with SessionLocal() as db:
            item = db.get(Item, item_id)
            if not item or item.user_id != user_id:
                raise ValueError("Item not found or ownership mismatch")

            listing = (
                db.query(ChannelListing)
                .filter(ChannelListing.item_id == item_id, ChannelListing.channel == marketplace)
                .first()
            )
            if not listing:
                listing = ChannelListing(
                    user_id=user_id,
                    item_id=item_id,
                    channel=marketplace,
                    status=ListingStatus.PUBLISH_QUEUED,
                )
                db.add(listing)
                db.flush()

            # Stub integration: set a synthetic external listing id as if marketplace accepted publish.
            listing.external_listing_id = f"{marketplace.value}-{item_id}-{int(datetime.now(timezone.utc).timestamp())}"
            listing.status = ListingStatus.LIVE
            listing.last_error = None
            listing.last_synced_at = datetime.now(timezone.utc)
            db.commit()
            listing_id = listing.id

        _log_sync_event(
            user_id=user_id,
            item_id=item_id,
            channel_listing_id=listing_id,
            order_id=None,
            job_id=job_id,
            event_type="publish_succeeded",
            status=EventStatus.SUCCEEDED,
            message=f"Publish stub succeeded for item {item_id} on {channel}",
            payload={"channel": channel, "listing_id": listing_id},
        )

        return {
            "item_id": item_id,
            "channel": channel,
            "status": "published",
            "job_id": job_id,
        }
    except Exception as exc:
        with SessionLocal() as db:
            listing_id = None
            if parsed_channel is not None:
                listing = (
                    db.query(ChannelListing)
                    .filter(ChannelListing.item_id == item_id, ChannelListing.channel == parsed_channel)
                    .first()
                )
            else:
                listing = None

            if listing is not None:
                listing.status = ListingStatus.ERROR
                listing.last_error = str(exc)
                listing.last_synced_at = datetime.now(timezone.utc)
                listing_id = listing.id
                db.commit()

        _log_sync_event(
            user_id=user_id,
            item_id=item_id,
            channel_listing_id=listing_id,
            order_id=None,
            job_id=job_id,
            event_type="publish_failed",
            status=EventStatus.FAILED,
            message=f"Publish failed for item {item_id} on {channel}: {exc}",
            payload={"channel": channel},
        )
        raise


@celery_app.task(bind=True, name="jobs.sync_orders")
def sync_orders(self, user_id: int, channel: str) -> dict:
    job_id = self.request.id
    _log_sync_event(
        user_id=user_id,
        item_id=None,
        channel_listing_id=None,
        order_id=None,
        job_id=job_id,
        event_type="sync_orders_started",
        status=EventStatus.STARTED,
        message=f"Order sync started for user {user_id} on {channel}",
        payload={"channel": channel},
    )

    try:
        _ = MarketplaceChannel(channel)
        synced_count = 0
        _log_sync_event(
            user_id=user_id,
            item_id=None,
            channel_listing_id=None,
            order_id=None,
            job_id=job_id,
            event_type="sync_orders_succeeded",
            status=EventStatus.SUCCEEDED,
            message=f"Order sync stub completed for user {user_id} on {channel}",
            payload={"channel": channel, "synced": synced_count},
        )
        return {"status": "ok", "synced": synced_count, "channel": channel, "job_id": job_id}
    except Exception as exc:
        _log_sync_event(
            user_id=user_id,
            item_id=None,
            channel_listing_id=None,
            order_id=None,
            job_id=job_id,
            event_type="sync_orders_failed",
            status=EventStatus.FAILED,
            message=f"Order sync failed for user {user_id} on {channel}: {exc}",
            payload={"channel": channel},
        )
        raise


@celery_app.task(bind=True, name="jobs.auto_delist")
def auto_delist(self, item_id: int, exclude_channel: str, user_id: int) -> dict:
    job_id = self.request.id
    _log_sync_event(
        user_id=user_id,
        item_id=item_id,
        channel_listing_id=None,
        order_id=None,
        job_id=job_id,
        event_type="auto_delist_started",
        status=EventStatus.STARTED,
        message=f"Auto-delist started for item {item_id}; excluding {exclude_channel}",
        payload={"exclude_channel": exclude_channel},
    )

    try:
        excluded = MarketplaceChannel(exclude_channel)
        with SessionLocal() as db:
            listings = (
                db.query(ChannelListing)
                .filter(
                    ChannelListing.item_id == item_id,
                    ChannelListing.user_id == user_id,
                    ChannelListing.channel != excluded,
                )
                .all()
            )
            for listing in listings:
                listing.status = ListingStatus.DELISTED
                listing.last_error = None
                listing.last_synced_at = datetime.now(timezone.utc)
            db.commit()

        _log_sync_event(
            user_id=user_id,
            item_id=item_id,
            channel_listing_id=None,
            order_id=None,
            job_id=job_id,
            event_type="auto_delist_succeeded",
            status=EventStatus.SUCCEEDED,
            message=f"Auto-delist stub completed for item {item_id}",
            payload={"exclude_channel": exclude_channel},
        )
        return {"status": "ok", "item_id": item_id, "job_id": job_id}
    except Exception as exc:
        _log_sync_event(
            user_id=user_id,
            item_id=item_id,
            channel_listing_id=None,
            order_id=None,
            job_id=job_id,
            event_type="auto_delist_failed",
            status=EventStatus.FAILED,
            message=f"Auto-delist failed for item {item_id}: {exc}",
            payload={"exclude_channel": exclude_channel},
        )
        raise
