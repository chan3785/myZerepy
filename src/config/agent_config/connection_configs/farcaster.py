from typing import Any, Optional
from pydantic import Field
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
from ...types import ApiKey, BlockchainNetwork
from .base_connection import BaseConnectionConfig, BaseConnectionSettings

from farcaster import Warpcast  # type: ignore


class FarcasterConnectionError(Exception):
    """Base exception for Farcaster connection errors"""

    pass


class FarcasterConfigurationError(FarcasterConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class FarcasterAPIError(FarcasterConnectionError):
    """Raised when Farcaster API requests fail"""

    pass


class FarcasterSettings(BaseConnectionSettings):
    mnemonic: ApiKey = Field(validation_alias="FARCASTER_MNEMONIC")


class FarcasterConfig(BaseConnectionConfig):
    timeline_read_count: int = 10
    cast_interval: int = 60
    farcaster_settings: FarcasterSettings = FarcasterSettings()  # type: ignore
    _client: Optional[Warpcast] = None

    def _get_client(self) -> Warpcast:
        if self._client is None:
            self._client = Warpcast(mnemonic=self.farcaster_settings.mnemonic)
        return self._client
