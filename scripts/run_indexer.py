"""
Standalone worker that polls the deployed contract for Mint/Transfer events and
writes them into Postgres (assets + events tables). Run this as a separate
process from the API server:

    python scripts/run_indexer.py

Prerequisites (once Monika shares her output — see novatrust-contracts):
  1. Put the contract's ABI JSON at CONTRACT_ABI_PATH (default ./contracts/NovaTrustAsset.json)
  2. Set CONTRACT_ADDRESS and RPC_URL in .env

This assumes an ERC-721-style contract with standard Transfer(from, to, tokenId)
events, treating a transfer from the zero address as a mint. Adjust `handle_transfer`
below if the actual contract emits a custom Mint event instead/as well.
"""
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from web3 import Web3

from app.config import settings
from app.database import SessionLocal
from app.services.chain import get_web3, get_contract
from app import models

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def handle_transfer(db, w3: Web3, event) -> None:
    args = event["args"]
    from_addr = args["from"]
    to_addr = args["to"]
    token_id = args["tokenId"]
    tx_hash = event["transactionHash"].hex()
    block_number = event["blockNumber"]
    is_mint = from_addr == ZERO_ADDRESS

    db.add(models.Event(
        event_type="Mint" if is_mint else "Transfer",
        actor_address=to_addr if is_mint else from_addr,
        target_token_id=token_id,
        tx_hash=tx_hash,
        block_number=block_number,
        details={"from": from_addr, "to": to_addr, "tokenId": token_id},
    ))

    if is_mint:
        existing = db.query(models.Asset).filter(models.Asset.token_id == token_id).first()
        if not existing:
            db.add(models.Asset(
                token_id=token_id,
                owner_address=to_addr,
                tx_hash=tx_hash,
            ))
    else:
        asset = db.query(models.Asset).filter(models.Asset.token_id == token_id).first()
        if asset:
            asset.owner_address = to_addr

    db.commit()
    print(f"[indexer] {'Mint' if is_mint else 'Transfer'} tokenId={token_id} tx={tx_hash}")


def main():
    w3 = get_web3()
    contract = get_contract()

    from_block = settings.indexer_start_block
    print(f"[indexer] starting from block {from_block}, polling every {settings.indexer_poll_seconds}s")

    while True:
        latest_block = w3.eth.block_number
        if latest_block >= from_block:
            logs = contract.events.Transfer.get_logs(from_block=from_block, to_block=latest_block)
            db = SessionLocal()
            try:
                for event in logs:
                    handle_transfer(db, w3, event)
            finally:
                db.close()
            from_block = latest_block + 1
        time.sleep(settings.indexer_poll_seconds)


if __name__ == "__main__":
    main()
