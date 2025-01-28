from typing import Any, Dict, Optional
from pydantic import Field

from src.config.base_config import BaseConfig
from .base_connection import BaseConnectionConfig, BaseConnectionSettings
from src.config.types import Rpc, EthereumPrivateKey
from goat import PluginBase, ToolBase, WalletClientBase, get_tools
from goat_wallets.web3 import Web3EVMWalletClient
from web3 import Web3
from eth_account import Account


class GoatConnectionError(Exception):
    """Base exception for Goat connection errors"""

    pass


class GoatConfigurationError(GoatConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class GoatAPIError(GoatConnectionError):
    """Raised when Goat API requests fail"""

    pass


class GoatPlugin(BaseConfig):
    name: str
    args: dict[str, Any]


class GoatSettings(BaseConnectionSettings):
    rpc: Rpc = Field(validation_alias="GOAT_RPC_PROVIDER_URL")
    private_key: EthereumPrivateKey = Field(validation_alias="GOAT_WALLET_PRIVATE_KEY")


class GoatConfig(BaseConnectionConfig):
    plugins: list[GoatPlugin]
    goat_settings: GoatSettings = GoatSettings()  # type: ignore
    _wallet_client: Optional[Web3EVMWalletClient] = None
    _action_registry: Dict[str, ToolBase] = {}

    def _get_client(self) -> Web3EVMWalletClient:

        if self._wallet_client is None:
            rpc_url = self.goat_settings.rpc
            private_key = self.goat_settings.private_key
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            account = Account.from_key(private_key)
            w3.eth.default_account = account.address
            self._wallet_client = Web3EVMWalletClient(w3)
        return self._wallet_client
