from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.channel_listing import ChannelListing
from app.models.enums import EventStatus, ListingStatus
from app.models.item import Item
from app.models.sync_event import SyncEvent
from app.models.user import User
from app.schemas.items import ItemCreate, ItemOut, ItemUpdate, PublishRequest, PublishResponse
from app.tasks.jobs import publish_item

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = Item(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        price_cents=payload.price_cents,
        currency=payload.currency.upper(),
        quantity=payload.quantity,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("", response_model=list[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ItemOut]:
    stmt = select(Item).where(Item.user_id == current_user.id).order_by(Item.created_at.desc())
    return list(db.scalars(stmt))


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = db.get(Item, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = db.get(Item, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        if key == "currency" and value is not None:
            value = value.upper()
        setattr(item, key, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item = db.get(Item, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    db.delete(item)
    db.commit()


@router.post("/{item_id}/publish", response_model=PublishResponse)
def publish_item_endpoint(
    item_id: int,
    payload: PublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PublishResponse:
    item = db.get(Item, item_id)
    if not item or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    listing = db.scalar(
        select(ChannelListing).where(
            ChannelListing.item_id == item.id,
            ChannelListing.channel == payload.channel,
        )
    )
    if not listing:
        listing = ChannelListing(
            user_id=current_user.id,
            item_id=item.id,
            channel=payload.channel,
            status=ListingStatus.PUBLISH_QUEUED,
            last_synced_at=datetime.now(timezone.utc),
        )
        db.add(listing)
        db.flush()
    else:
        listing.status = ListingStatus.PUBLISH_QUEUED
        listing.last_error = None
        listing.last_synced_at = datetime.now(timezone.utc)

    task = publish_item.delay(item_id=item.id, channel=payload.channel.value, user_id=current_user.id)

    db.add(
        SyncEvent(
            user_id=current_user.id,
            item_id=item.id,
            channel_listing_id=listing.id,
            job_id=task.id,
            event_type="publish_requested",
            status=EventStatus.STARTED,
            message=f"Publish requested for {payload.channel.value}",
            payload={"channel": payload.channel.value},
        )
    )
    db.commit()

    return PublishResponse(job_id=task.id, item_id=item.id, channel=payload.channel)
