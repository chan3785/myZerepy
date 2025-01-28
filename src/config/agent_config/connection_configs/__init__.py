import json
from typing import Any, Optional

from pydantic import ValidationError
from pydantic_core import ErrorDetails

from ...base_config import BaseConfig, BaseSettings

from .twitter import TwitterConfig
from .solana import SolanaConfig
from .allora import AlloraConfig
from .farcaster import FarcasterConfig
from .goat import GoatConfig
from .base_connection import CONNECTION_ERRORS
import click
from src.lib import deep_pretty_print


class InvalidConnectionConfigError(Exception):
    """Raised when there are configuration/credential issues"""

    pass


class ConnectionsSettings(BaseSettings):
    pass


class ConnectionsConfig(BaseConfig):
    twitter: Optional[TwitterConfig] = None
    solana: Optional[SolanaConfig] = None
    allora: Optional[AlloraConfig] = None
    farcaster: Optional[FarcasterConfig] = None
    goat: Optional[GoatConfig] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._validate()

    def _validate(self) -> None:
        errors: dict[str, list[ErrorDetails]] = CONNECTION_ERRORS
        res_str = ""
        for k, v in errors.items():
            res_str += f"\n{k}:\n"
            for e in v:
                res_str += f"{'.'.join(map(str, e.get('loc', [])))} : {e.get('msg')}\n"
        if res_str:
            click.secho(click.style(res_str, fg="red", bold=True))
