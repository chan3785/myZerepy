from typing import Any
from pydantic import Field
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from .base_model import BaseModelSettings, BaseModelConfig
import os


class HyperbolicConnectionError(Exception):
    """Base exception for Hyperbolic connection errors"""

    pass


class HyperbolicConfigurationError(HyperbolicConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class HyperbolicAPIError(HyperbolicConnectionError):
    """Raised when Hyperbolic API requests fail"""

    pass


class HyperbolicSettings(BaseModelSettings):
    api_key: ApiKey = Field(validation_alias="HYPERBOLIC_API_KEY")


class HyperbolicConfig(BaseModelConfig):
    hyperbolic_settings: HyperbolicSettings = HyperbolicSettings()  # type: ignore

    def _get_client(self) -> None:
        return None
