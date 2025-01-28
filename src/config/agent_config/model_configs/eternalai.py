from typing import Any
from pydantic import Field
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from .base_model import BaseModelSettings, BaseModelConfig
import os


class EternalAIConnectionError(Exception):
    """Base exception for EternalAI connection errors"""

    pass


class EternalAIConfigurationError(EternalAIConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class EternalAIAPIError(EternalAIConnectionError):
    """Raised when EternalAI API requests fail"""

    pass


class EternalAISettings(BaseModelSettings):
    api_key: ApiKey = Field(validation_alias="ETERNALAI_API_KEY")


class EternalAIConfig(BaseModelConfig):
    chain_id: int
    eternalai_settings: EternalAISettings = EternalAISettings()  # type: ignore

    def _get_client(self) -> None:
        return None
