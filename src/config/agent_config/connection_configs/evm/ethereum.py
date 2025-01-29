from typing import Any
from pydantic import Field
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
import asyncio
from .base_evm_connection import BaseEvmConfig, BaseEvmSettings
from ....types import EthereumPrivateKey


class EthereumSettings(BaseEvmSettings):
    private_key: EthereumPrivateKey = Field(validation_alias="ETHEREUM_API_KEY")


class EthereumConfig(BaseEvmConfig):
    ethereum_settings: EthereumSettings = EthereumSettings()  # type: ignore
