from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.sync_event import SyncEvent
from app.models.user import User
from app.schemas.events import SyncEventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[SyncEventOut])
def list_events(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SyncEventOut]:
    stmt = (
        select(SyncEvent)
        .where(SyncEvent.user_id == current_user.id)
        .order_by(SyncEvent.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))
