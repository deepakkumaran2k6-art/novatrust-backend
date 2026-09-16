"""
IPFS pinning via Pinata. If no Pinata keys are set in .env, falls back to a mock
hash so the rest of the app (and Fathima's frontend) can be built and demoed
before real IPFS credentials exist.
"""
import hashlib

import requests

from app.config import settings

PINATA_PIN_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
GATEWAY = "https://gateway.pinata.cloud/ipfs/"


def pin_file(file_bytes: bytes, filename: str) -> tuple[str, bool]:
    """Returns (ipfs_hash, was_mocked)."""
    if not settings.pinata_api_key or not settings.pinata_secret_api_key:
        # Mock mode: deterministic fake hash so repeated uploads of the same file are stable.
        fake_hash = "Qm" + hashlib.sha256(file_bytes).hexdigest()[:44]
        return fake_hash, True

    headers = {
        "pinata_api_key": settings.pinata_api_key,
        "pinata_secret_api_key": settings.pinata_secret_api_key,
    }
    files = {"file": (filename, file_bytes)}
    resp = requests.post(PINATA_PIN_URL, files=files, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["IpfsHash"], False


def gateway_url(ipfs_hash: str) -> str:
    return f"{GATEWAY}{ipfs_hash}"
