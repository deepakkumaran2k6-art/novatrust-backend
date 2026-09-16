from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["roles"])


@router.get("/roles/{address}", response_model=schemas.RoleOut)
def get_role(address: str, db: Session = Depends(get_db)):
    role = db.query(models.Role).filter(models.Role.address == address).first()
    if not role:
        # Default to "user" rather than 404 — every address is at least a viewer.
        return schemas.RoleOut(address=address, role="user", updated_at=datetime.now(timezone.utc))
    return role


@router.post("/roles", response_model=schemas.RoleOut)
def set_role(payload: schemas.RoleSetIn, db: Session = Depends(get_db)):
    """
    MVP/demo convenience endpoint to assign a role off-chain.
    TODO: once on-chain RBAC (Monika's contracts) is live, gate this behind an
    admin check and/or sync it from on-chain RoleGranted events instead.
    """
    role = db.query(models.Role).filter(models.Role.address == payload.address).first()
    if role:
        role.role = payload.role
    else:
        role = models.Role(address=payload.address, role=payload.role)
        db.add(role)
    db.commit()
    db.refresh(role)
    return role
