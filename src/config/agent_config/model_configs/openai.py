from typing import Any
from pydantic import Field
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from .base_model import BaseModelSettings, BaseModelConfig
import os
from openai import OpenAI


class OpenAIConnectionError(Exception):
    """Base exception for OpenAI connection errors"""

    pass


class OpenAIConfigurationError(OpenAIConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class OpenAIAPIError(OpenAIConnectionError):
    """Raised when OpenAI API requests fail"""

    pass


class OpenAiSettings(BaseModelSettings):
    api_key: ApiKey = Field(validation_alias="OPENAI_API_KEY")


class OpenAiConfig(BaseModelConfig):
    openai_settings: OpenAiSettings = OpenAiSettings()  # type: ignore

    def _get_client(self) -> OpenAI:
        """Get or create OpenAI client"""
        return OpenAI(api_key=self.openai_settings.api_key)
