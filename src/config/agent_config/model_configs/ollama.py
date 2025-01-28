from typing import Any
from pydantic import Field
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from .base_model import BaseModelSettings, BaseModelConfig
import os
from ...types import Rpc


class OllamaConnectionError(Exception):
    """Base exception for Ollama connection errors"""

    pass


class OllamaConfigurationError(OllamaConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class OllamaAPIError(OllamaConnectionError):
    """Raised when Ollama API requests fail"""

    pass


class OllamaSettings(BaseModelSettings):
    api_key: ApiKey = Field(validation_alias="OLLAMA_API_KEY")


class OllamaConfig(BaseModelConfig):
    base_url: Rpc
    ollama_settings: OllamaSettings = OllamaSettings()  # type: ignore

    def _get_client(self) -> None:
        return None
