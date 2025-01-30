from typing import Any
from pydantic import Field
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
from src.config.types import ApiKey
from .base_connection import BaseConnectionConfig, BaseConnectionSettings
from allora_sdk.v2.api_client import AlloraAPIClient, ChainSlug


class AlloraSettings(BaseConnectionSettings):
    api_key: ApiKey = Field(validation_alias="ALLORA_API_KEY")


class AlloraConfig(BaseConnectionConfig):
    chain_slug: ChainSlug
    allora_settings: AlloraSettings = AlloraSettings()  # type: ignore

    def _get_client(self) -> AlloraAPIClient:
        return AlloraAPIClient(
            chain_slug=self.chain_slug,
            api_key=self.allora_settings.api_key
        )

    def format_inference_data(self, inference_data: Any) -> dict:
        return {
            "inference": inference_data.network_inference_normalized
        }