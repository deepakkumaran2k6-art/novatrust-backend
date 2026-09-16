from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["audit"])


@router.get("/audit-log", response_model=list[schemas.EventOut])
def get_audit_log(
    actor: Optional[str] = Query(None, description="Filter by actor address"),
    event_type: Optional[str] = Query(None, description="Filter by event type, e.g. Mint"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(models.Event)
    if actor:
        q = q.filter(models.Event.actor_address == actor)
    if event_type:
        q = q.filter(models.Event.event_type == event_type)
    return q.order_by(models.Event.timestamp.desc()).offset(skip).limit(limit).all()
