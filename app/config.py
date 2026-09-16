"""
Central settings, loaded from environment variables / .env.
Import `settings` anywhere you need config instead of reading os.environ directly.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://novatrust:novatrust@localhost:5432/novatrust"

    # Blockchain
    rpc_url: str = ""
    contract_address: str = ""
    contract_abi_path: str = "./contracts/NovaTrustAsset.json"
    indexer_start_block: int = 0
    indexer_poll_seconds: int = 8

    # IPFS (Pinata)
    pinata_api_key: str = ""
    pinata_secret_api_key: str = ""

    # CORS
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
