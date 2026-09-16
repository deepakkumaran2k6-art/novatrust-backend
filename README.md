# novatrust-backend

Backend API for **NovaTrust** (SIH26125) — indexes on-chain events from the
`novatrust-contracts` repo, serves asset/audit data to `novatrust-frontend`,
and handles IPFS storage and off-chain k-of-n threshold-approval tracking.

## Stack
FastAPI · SQLAlchemy · PostgreSQL · web3.py · Pinata (IPFS)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then fill in DATABASE_URL at minimum
```

Create the database (adjust to your local Postgres setup):

```bash
createdb novatrust
```

Run the API:

```bash
uvicorn app.main:app --reload
```

- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Tables are created automatically on startup from `app/models.py` (no
migrations yet — fine for hackathon speed, revisit with Alembic if the
schema needs to evolve after data already exists).

## Once contracts are deployed (Monika's output)

1. Save the ABI JSON to `contracts/NovaTrustAsset.json`
2. Set `CONTRACT_ADDRESS` and `RPC_URL` in `.env`
3. Run the indexer in a separate terminal:

```bash
python scripts/run_indexer.py
```

It polls for `Transfer` events (treating a transfer from the zero address as
a mint) and writes them into the `assets` and `events` tables.

## IPFS

`/upload` pins files to IPFS via Pinata. Without `PINATA_API_KEY` /
`PINATA_SECRET_API_KEY` set, it returns a deterministic **mock** hash so the
frontend can be built against it before real credentials exist — the
response includes `"mock": true` in that case.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/assets` | List minted assets |
| GET | `/assets/{token_id}` | Get one asset |
| GET | `/verify/{token_id}` | Public verification (e.g. for an employer) |
| GET | `/audit-log` | Timeline of indexed on-chain events |
| GET | `/roles/{address}` | Look up an address's role |
| POST | `/roles` | Set an address's role (demo/off-chain) |
| POST | `/approvals` | Propose a critical action needing k-of-n sign-off |
| POST | `/approvals/{id}/sign` | Add a signer's approval |
| GET | `/approvals/{id}` | Check approval status |
| POST | `/upload` | Pin a file to IPFS |

## Tests

```bash
pytest
```

## Sharing progress with the team

Per the team's GitHub workflow guide: once this is deployed (Render/Railway/ngrok),
post the live API URL in the team chat so Fathima can connect the frontend
without waiting for the final repo merge.
