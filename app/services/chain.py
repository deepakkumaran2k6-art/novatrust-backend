"""
Blockchain connection helper.

Once Monika shares the deployed contract's address + ABI:
  1. Save the ABI JSON as ./contracts/NovaTrustAsset.json (just the `abi` array, or the
     full Hardhat artifact — get_contract() handles either).
  2. Put the address in CONTRACT_ADDRESS in your .env.
  3. get_contract() below will pick both up automatically.
"""
import json
import os
from functools import lru_cache

from web3 import Web3

from app.config import settings


@lru_cache
def get_web3() -> Web3:
    if not settings.rpc_url:
        raise RuntimeError(
            "RPC_URL is not set in .env — get a free Sepolia RPC URL from Alchemy or Infura."
        )
    return Web3(Web3.HTTPProvider(settings.rpc_url))


def _load_abi(path: str) -> list:
    with open(path) as f:
        data = json.load(f)
    # Hardhat artifacts wrap the ABI in {"abi": [...]}; plain ABI files are just the array.
    return data["abi"] if isinstance(data, dict) and "abi" in data else data


@lru_cache
def get_contract():
    if not settings.contract_address:
        raise RuntimeError(
            "CONTRACT_ADDRESS is not set in .env yet — ask Monika for the deployed address."
        )
    if not os.path.exists(settings.contract_abi_path):
        raise RuntimeError(
            f"ABI file not found at {settings.contract_abi_path} — save the ABI Monika shares there."
        )
    w3 = get_web3()
    abi = _load_abi(settings.contract_abi_path)
    return w3.eth.contract(address=Web3.to_checksum_address(settings.contract_address), abi=abi)
