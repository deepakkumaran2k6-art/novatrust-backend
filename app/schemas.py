from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ---------- Assets ----------
class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token_id: int
    owner_address: str
    ipfs_hash: Optional[str] = None
    asset_metadata: Optional[dict] = None
    tx_hash: Optional[str] = None
    minted_at: datetime


class VerifyOut(BaseModel):
    verified: bool
    token_id: int
    owner_address: Optional[str] = None
    ipfs_hash: Optional[str] = None
    minted_at: Optional[datetime] = None
    message: Optional[str] = None


# ---------- Events / audit log ----------
class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    actor_address: Optional[str] = None
    target_token_id: Optional[int] = None
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: datetime
    details: Optional[dict] = None


# ---------- Roles ----------
class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    address: str
    role: str
    updated_at: datetime


class RoleSetIn(BaseModel):
    address: str
    role: str  # "admin" | "manager" | "auditor" | "user"


# ---------- Threshold approvals ----------
class ApprovalRequestCreateIn(BaseModel):
    action_type: str
    payload: Optional[dict[str, Any]] = None
    required_approvals: int = 2
    created_by: Optional[str] = None


class ApprovalIn(BaseModel):
    signer_address: str


class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    signer_address: str
    signed_at: datetime


class ApprovalRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action_type: str
    payload: Optional[dict] = None
    required_approvals: int
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    approvals: list[ApprovalOut] = []


# ---------- IPFS ----------
class UploadOut(BaseModel):
    ipfs_hash: str
    gateway_url: str
    mock: bool = False
