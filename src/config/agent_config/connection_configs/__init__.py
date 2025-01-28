from .twitter import TwitterConfig
from .solana import SolanaConfig
from .allora import AlloraConfig
from typing import Optional
from ...base_config import BaseConfig, BaseSettings
from datetime import datetime
from typing import Annotated, Any, Optional, Tuple, TypeAliasType
from ...base_config import BaseConfig, BaseSettings
from pydantic import (
    PositiveFloat,
    TypeAdapter,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from .base_connection import BaseConnectionConfig


class ConnectionsSettings(BaseSettings):
    pass


class ConnectionsConfig(BaseConfig):
    twitter: Optional[TwitterConfig] = None
    solana: Optional[SolanaConfig] = None
    allora: Optional[AlloraConfig] = None
