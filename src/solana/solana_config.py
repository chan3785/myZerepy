import json
from typing import Any, Dict
from src.lib.base_config import BaseConfig
from src.agent.agent_config import AgentConfig
from src.lib.base_connection import BaseConnectionConfig
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from jupiter_python_sdk.jupiter import Jupiter


from src.utils.deep_dict import deep_get


class SolanaConfig(BaseConnectionConfig):
    agent_config: AgentConfig
    client: AsyncClient
    wallet: Keypair
    jupiter: Jupiter

    def __init__(self, agent_name: str) -> None:
        self.agent_config = AgentConfig(agent_name)
        super().__init__(self.agent_config.cfg)
        self.wallet = self.get_wallet()
        self.client = self.get_client()
        self.jupiter = self.get_jupiter()

    @property
    def is_llm_provider(self) -> bool:
        return False

    @staticmethod
    def config_key() -> str:
        return "solana"

    @staticmethod
    def required_config_fields() -> Dict[str, type[Any]]:
        return {
            "rpc": str,
        }

    @staticmethod
    def required_env_vars() -> Dict[str, type[Any]]:
        return {
            "SOLANA_PRIVATE_KEY": str,
        }

    @staticmethod
    def required_fields() -> Dict[str, type[Any]]:
        return {
            **SolanaConfig.required_config_fields(),
            **SolanaConfig.required_env_vars(),
        }

    def get_client(self) -> AsyncClient:
        conn = AsyncClient(self.get("rpc"))
        return conn

    def get_wallet(self) -> Keypair:
        try:
            return Keypair.from_base58_string(self.cfg["SOLANA_PRIVATE_KEY"])
        except Exception as e:
            raise Exception(f"Failed to get wallet: {str(e)}")

    def get_jupiter(self) -> Jupiter:
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
