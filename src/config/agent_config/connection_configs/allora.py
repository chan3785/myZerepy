from typing import Any
from pydantic import Field
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
from ...types import ApiKey, BlockchainNetwork
from .base_connection import BaseConnectionConfig, BaseConnectionSettings
from allora_sdk.v2.api_client import AlloraAPIClient, ChainSlug
import asyncio


class AlloraConnectionError(Exception):
    """Base exception for Allora connection errors"""

    pass


class AlloraConfigurationError(AlloraConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class AlloraAPIError(AlloraConnectionError):
    """Raised when Allora API requests fail"""

    pass


class AlloraSettings(BaseConnectionSettings):
    api_key: ApiKey = Field(validation_alias="ALLORA_API_KEY")


class AlloraConfig(BaseConnectionConfig):
    chain: BlockchainNetwork
    allora_settings: AlloraSettings = AlloraSettings()  # type: ignore

    def _get_client(self) -> AlloraAPIClient:
        return AlloraAPIClient(
            chain_slug=self.chain, api_key=self.allora_settings.api_key
        )

    def _make_request(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        try:
            client = self._get_client()
            method = getattr(client, method_name)

            # Create event loop for async calls
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(method(*args, **kwargs))
                return response
            finally:
                loop.close()

        except Exception as e:
            raise AlloraAPIError(f"API request failed: {str(e)}")