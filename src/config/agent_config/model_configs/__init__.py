import click
from pydantic_core import ErrorDetails
from ...base_config import BaseConfig, BaseSettings
from typing import Any, Optional
from .base_model import MODEL_ERRORS
from .openai import OpenAIConfig
from .anthropic import AnthropicConfig
from .ollama import OllamaConfig
from .hyperbolic import HyperbolicConfig
from .galadriel import GaladrielConfig
from .eternalai import EternalAIConfig


class ModelsSettings(BaseConfig, BaseSettings):
    pass


class ModelsConfig(BaseConfig):
    openai: Optional[OpenAIConfig] = None
    anthropic: Optional[AnthropicConfig] = None
    ollama: Optional[OllamaConfig] = None
    hyperbolic: Optional[HyperbolicConfig] = None
    galadriel: Optional[GaladrielConfig] = None
    eternalai: Optional[EternalAIConfig] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._validate()

    def _validate(self) -> None:
        errors: dict[str, list[ErrorDetails]] = MODEL_ERRORS
        res_str = ""
        for k, v in errors.items():
            res_str += f"\n{k}:\n"
            for e in v:
                res_str += f"{'.'.join(map(str, e.get('loc', [])))} : {e.get('msg')}\n"
        if res_str:
            click.secho(click.style(res_str, fg="red", bold=True))
