from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Asset(Base):
    """A minted NFT asset (certificate, equipment record, etc.)."""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, unique=True, index=True, nullable=False)
    owner_address = Column(String, index=True, nullable=False)
    ipfs_hash = Column(String, nullable=True)
    asset_metadata = Column(JSON, nullable=True)  # free-form: name, type, description...
    tx_hash = Column(String, nullable=True)
    minted_at = Column(DateTime, default=utcnow)


class Event(Base):
    """Every on-chain action we've indexed — powers the audit-log endpoint."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False)  # "Mint" | "Transfer" | "RoleGranted" | ...
    actor_address = Column(String, index=True, nullable=True)
    target_token_id = Column(Integer, nullable=True)
    tx_hash = Column(String, index=True, nullable=True)
    block_number = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=utcnow, index=True)
    details = Column(JSON, nullable=True)


class Role(Base):
    """Off-chain role lookup — keep in sync with whatever the contracts enforce on-chain."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False, default="user")  # "admin" | "manager" | "auditor" | "user"
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class ApprovalRequest(Base):
    """A proposed critical action awaiting k-of-n sign-off before it's submitted on-chain."""
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, nullable=False)  # "mint" | "revoke" | "transfer" | ...
    payload = Column(JSON, nullable=True)
    required_approvals = Column(Integer, nullable=False, default=2)
    status = Column(String, nullable=False, default="pending")  # pending | approved | executed | rejected
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    approvals = relationship("Approval", back_populates="request", cascade="all, delete-orphan")


class Approval(Base):
    """A single signer's sign-off on an ApprovalRequest."""
    __tablename__ = "approvals"
    __table_args__ = (UniqueConstraint("request_id", "signer_address", name="uq_request_signer"),)

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=False)
    signer_address = Column(String, nullable=False)
    signed_at = Column(DateTime, default=utcnow)

    request = relationship("ApprovalRequest", back_populates="approvals")
