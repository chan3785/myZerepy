from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from src.lib.types import Rpc, SolanaPrivateKey


class SolanaSettings(BaseSettings):
    private_key: SolanaPrivateKey = Field(validation_alias="SOLANA_PRIVATE_KEY")


class SolanaConfig(BaseModel):
    rpc: Rpc
    solana_settings: SolanaSettings

    def __init__(self, **data) -> None:
        # if the connection is not configured, return none
        try:
            data["solana_settings"] = SolanaSettings()
            super().__init__(**data)
        except Exception as e:
            return
