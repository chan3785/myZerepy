from typing import Any
from pydantic import Field
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from .base_model import BaseModelSettings, BaseModelConfig
import os


class AnthropicConnectionError(Exception):
    """Base exception for Anthropic connection errors"""

    pass


class AnthropicConfigurationError(AnthropicConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class AnthropicAPIError(AnthropicConnectionError):
    """Raised when Anthropic API requests fail"""

    pass


class AnthropicSettings(BaseModelSettings):
    api_key: ApiKey = Field(validation_alias="ANTHROPIC_API_KEY")


class AnthropicConfig(BaseModelConfig):
    anthropic_settings: AnthropicSettings = AnthropicSettings()  # type: ignore

    def _get_client(self) -> None:
        return None
