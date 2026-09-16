from fastapi import APIRouter, UploadFile, File

from app import schemas
from app.services.ipfs_client import pin_file, gateway_url

router = APIRouter(tags=["ipfs"])


@router.post("/upload", response_model=schemas.UploadOut)
async def upload_file(file: UploadFile = File(...)):
    """
    Pin a file (e.g. a certificate PDF) to IPFS. Returns the hash to embed in the
    mint transaction's metadata. Falls back to a mock hash if Pinata keys aren't
    set yet in .env, so the frontend can be built against this before real IPFS
    credentials exist.
    """
    contents = await file.read()
    ipfs_hash, was_mocked = pin_file(contents, file.filename)
    return schemas.UploadOut(ipfs_hash=ipfs_hash, gateway_url=gateway_url(ipfs_hash), mock=was_mocked)
