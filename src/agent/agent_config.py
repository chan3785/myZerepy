import os
from pathlib import Path
from typing import Any, Dict
from src.lib.base_config import BaseConfig
import json
import logging


logger = logging.getLogger(__name__)


class AgentConfig(BaseConfig):
    default_agent_name = "example"

    def __init__(self, agent_name: str) -> None:
        agent_path = AgentConfig.path() / f"{agent_name}.json"
        data = json.load(open(agent_path, "r"))
        super().__init__(data)

    @property
    def is_llm_provider(self) -> bool:
        return False

    @staticmethod
    def required_config_fields() -> Dict[str, type[Any]]:
        return {
            "name": str,
            "bio": list[str],
            "traits": list[str],
            "examples": list[str],
            "example_accounts": list[str],
            "loop_delay": int,
            "connections": dict[str, dict[str, Any]],
            "tasks": list[dict[str, dict[str, Any]]],
            "use_time_based_weights": bool,
            "time_based_multipliers": dict[str, float],
        }

    @staticmethod
    def required_env_vars() -> Dict[str, type[Any]]:
        return {
            "TWITTER_USERNAME": str,
        }

    @staticmethod
    def required_fields() -> Dict[str, type[Any]]:
        return {
            **AgentConfig.required_config_fields(),
            **AgentConfig.required_env_vars(),
        }

    @staticmethod
    def is_valid_config(agent_name: str) -> bool:
        try:
            AgentConfig(agent_name)
            return True
        except Exception as e:
            return False

    @staticmethod
    def configs() -> list[str]:
        configs_path = AgentConfig.path()
        return [path.stem for path in configs_path.iterdir() if path.suffix == ".json"]
