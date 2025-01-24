import os
from pathlib import Path
from typing import Any, Dict
from src.lib.base_config import BaseConfig
import json
import logging
from pydantic import BaseModel, PositiveInt


logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    name: str
    bio: list[str]
    traits: list[str]
    examples: list[str]
    example_accounts: list[str]
    loop_delay: PositiveInt
    connections: dict[str, dict[str, Any]]
    tasks: list[dict[str, dict[str, Any]]]
    use_time_based_weights: bool
    time_based_multipliers: dict[str, float]

    @staticmethod
    def supported_file_extensions() -> list[str]:
        return [".json"]

    @staticmethod
    def from_path(path: Path) -> "AgentConfig":
        with open(path) as f:
            config = json.load(f)
        return AgentConfig(config)

    @property
    def is_llm_provider(self) -> bool:
        return False

    @staticmethod
    def required_env_vars() -> Dict[str, type[Any]]:
        return {
            "TWITTER_USERNAME": str,
        }
