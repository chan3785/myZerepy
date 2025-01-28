from .twitter import TwitterConfig
from .solana import SolanaConfig
from .allora import AlloraConfig
from typing import Optional
from ...base_config import BaseConfig, BaseSettings


class ConnectionsSettings(BaseSettings):
    pass


class ConnectionsConfig(BaseConfig):
    twitter: Optional[TwitterConfig] = None
    solana: Optional[SolanaConfig] = None
    allora: Optional[AlloraConfig] = None
