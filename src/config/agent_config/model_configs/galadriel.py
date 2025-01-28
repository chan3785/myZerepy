from typing import Any
from pydantic import Field
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from .base_model import BaseModelSettings, BaseModelConfig
import os


class GaladrielConnectionError(Exception):
    """Base exception for Galadriel connection errors"""

    pass


class GaladrielConfigurationError(GaladrielConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class GaladrielAPIError(GaladrielConnectionError):
    """Raised when Galadriel API requests fail"""

    pass


class GaladrielSettings(BaseModelSettings):
    api_key: ApiKey = Field(validation_alias="GALADRIEL_API_KEY")


class GaladrielConfig(BaseModelConfig):
    galadriel_settings: GaladrielSettings = GaladrielSettings()  # type: ignore

    def _get_client(self) -> None:
        return None
