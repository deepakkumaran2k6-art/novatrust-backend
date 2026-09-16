from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["approvals"])


@router.post("/approvals", response_model=schemas.ApprovalRequestOut)
def create_approval_request(payload: schemas.ApprovalRequestCreateIn, db: Session = Depends(get_db)):
    """Propose a critical action (mint / revoke / transfer) that needs k-of-n sign-off."""
    req = models.ApprovalRequest(
        action_type=payload.action_type,
        payload=payload.payload,
        required_approvals=payload.required_approvals,
        created_by=payload.created_by,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/approvals", response_model=list[schemas.ApprovalRequestOut])
def list_approval_requests(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.ApprovalRequest)
    if status:
        q = q.filter(models.ApprovalRequest.status == status)
    return q.order_by(models.ApprovalRequest.created_at.desc()).all()


@router.get("/approvals/{request_id}", response_model=schemas.ApprovalRequestOut)
def get_approval_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(models.ApprovalRequest).filter(models.ApprovalRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return req


@router.post("/approvals/{request_id}/sign", response_model=schemas.ApprovalRequestOut)
def sign_approval_request(request_id: int, payload: schemas.ApprovalIn, db: Session = Depends(get_db)):
    req = db.query(models.ApprovalRequest).filter(models.ApprovalRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {req.status}")

    already_signed = any(a.signer_address == payload.signer_address for a in req.approvals)
    if already_signed:
        raise HTTPException(status_code=400, detail="This address has already signed")

    db.add(models.Approval(request_id=req.id, signer_address=payload.signer_address))
    db.commit()
    db.refresh(req)

    if len(req.approvals) >= req.required_approvals:
        req.status = "approved"
        db.commit()
        db.refresh(req)
        # TODO: once contracts are wired up, this is where you'd trigger the actual
        # on-chain transaction (or notify whoever holds the final "execute" button).

    return req
