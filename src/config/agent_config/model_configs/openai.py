from typing import Any
from pydantic import Field
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from .base_model import BaseModelSettings, BaseModelConfig


class OpenAiSettings(BaseModelSettings):
    api_key: ApiKey = Field(validation_alias="OPENAI_API_KEY")


class OpenAiConfig(BaseModelConfig):
    openai_settings: OpenAiSettings = OpenAiSettings()  # type: ignore
