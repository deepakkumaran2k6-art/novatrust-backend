from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import assets, audit, roles, approvals, ipfs

app = FastAPI(
    title="NovaTrust Backend",
    description="Backend API for NovaTrust (SIH26125) — indexes on-chain events, "
                "serves asset/audit data to the frontend, and coordinates IPFS storage "
                "and off-chain threshold-approval workflows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assets.router)
app.include_router(audit.router)
app.include_router(roles.router)
app.include_router(approvals.router)
app.include_router(ipfs.router)


@app.on_event("startup")
def on_startup():
    # MVP: create tables directly from the models. Swap for Alembic migrations
    # once the schema stabilizes and you need versioned changes.
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
