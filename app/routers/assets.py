from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["assets"])


@router.get("/assets", response_model=list[schemas.AssetOut])
def list_assets(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(models.Asset)
        .order_by(models.Asset.minted_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/assets/{token_id}", response_model=schemas.AssetOut)
def get_asset(token_id: int, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.token_id == token_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.get("/verify/{token_id}", response_model=schemas.VerifyOut)
def verify_asset(token_id: int, db: Session = Depends(get_db)):
    """Public verification endpoint — e.g. an employer checking a certificate."""
    asset = db.query(models.Asset).filter(models.Asset.token_id == token_id).first()
    if not asset:
        return schemas.VerifyOut(
            verified=False, token_id=token_id, message="No asset found with this token ID."
        )
    return schemas.VerifyOut(
        verified=True,
        token_id=asset.token_id,
        owner_address=asset.owner_address,
        ipfs_hash=asset.ipfs_hash,
        minted_at=asset.minted_at,
        message="Asset verified on-chain.",
    )
