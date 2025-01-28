from typing import Any
from pydantic import Field
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
from ...types import ApiKey, BlockchainNetwork
from .base_connection import BaseConnectionConfig, BaseConnectionSettings


class AlloraSettings(BaseConnectionSettings):
    api_key: ApiKey = Field(validation_alias="ALLORA_API_KEY")


class AlloraConfig(BaseConnectionConfig):
    chain: BlockchainNetwork
    allora_settings: AlloraSettings
