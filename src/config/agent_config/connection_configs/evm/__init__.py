import json
from typing import Any, Optional

from pydantic import ValidationError
from pydantic_core import ErrorDetails

import click
from src.config.base_config import BaseConfig, BaseSettings
from src.lib import deep_pretty_print
from .base_evm_connection import EVM_CONNECTION_ERRORS
from .ethereum import EthereumConfig


class InvalidEvmConnectionConfigError(Exception):
    """Raised when there are configuration/credential issues"""

    pass


class EvmConnectionsSettings(BaseSettings):
    pass


class EvmConnectionsConfig(BaseConfig):
    ethereum: Optional[EthereumConfig] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._validate()

    def _validate(self) -> None:
        errors: dict[str, list[ErrorDetails]] = EVM_CONNECTION_ERRORS
        res_str = ""
        for k, v in errors.items():
            res_str += f"\n{k}:\n"
            for e in v:
                res_str += f"{'.'.join(map(str, e.get('loc', [])))} : {e.get('msg')}\n"
        if res_str:
            click.secho(click.style(res_str, fg="red", bold=True))
