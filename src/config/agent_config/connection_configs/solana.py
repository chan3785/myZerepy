import logging
from typing import Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
from src.config.types import Rpc, SolanaPrivateKey
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from jupiter_python_sdk.jupiter import Jupiter
from pydantic_core import ErrorDetails
from pydantic import ValidationError


class SolanaSettings(BaseSettings):
    private_key: SolanaPrivateKey = Field(validation_alias="SOLANA_PRIVATE_KEY")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


class SolanaConfig(BaseConnectionConfig):
    rpc: Rpc
    solana_settings: SolanaSettings
    logger: logging.Logger

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        # if the connection is not configured, return none
        try:
            data["logger"] = logging.getLogger(f"{self.__class__.__name__}")
            data["solana_settings"] = SolanaSettings()
            super().__init__(**data)

        except Exception as e:
            if isinstance(e, ValidationError):
                errors: list[ErrorDetails] = e.errors()
                for error in errors:
                    print(
                        f'{error.get("msg")}. Invalid Field(s): {".".join(map(str, error.get("loc", [])))}'
                    )
            return

    def get_client(self) -> AsyncClient:
        self.logger.debug("Creating AsyncClient instance")
        conn = AsyncClient(self.rpc)
        return conn

    def get_wallet(self) -> Keypair:
        self.logger.debug("Creating Keypair instance")
        return self.solana_settings.private_key

    def get_jupiter(self) -> Jupiter:
        self.logger.debug("Creating Jupiter instance")
        jupiter = Jupiter(
            async_client=self.get_client(),
            keypair=self.get_wallet(),
            quote_api_url="https://quote-api.jup.ag/v6/quote?",
            swap_api_url="https://quote-api.jup.ag/v6/swap",
            open_order_api_url="https://jup.ag/api/limit/v1/createOrder",
            cancel_orders_api_url="https://jup.ag/api/limit/v1/cancelOrders",
            query_open_orders_api_url="https://jup.ag/api/limit/v1/openOrders?wallet=",
            query_order_history_api_url="https://jup.ag/api/limit/v1/orderHistory",
            query_trade_history_api_url="https://jup.ag/api/limit/v1/tradeHistory",
        )
        return jupiter

    def format_txid_to_scanner_url(self, txid: str) -> str:
        return f"https://explorer.solana.com/tx/{txid}"

    def to_json(self) -> dict[str, Any]:
        self.logger.debug("Serializing SolanaConfig")
        # we need to manually serialize the keypair
        wallet = str(self.get_wallet().pubkey())
        return {
            "rpc": self.rpc,
            "solana_settings": {"public_key": wallet},
        }

    @property
    def is_llm_provider(self) -> bool:
        return False
