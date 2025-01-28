import json
import logging
import os
from pathlib import Path
from pydantic import Field, PositiveFloat
from pydantic_core import ValidationError
from typing import Any, List, Dict, Optional

from dotenv import load_dotenv
import yaml  # type: ignore
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
from src.config.agent_config.model_configs.base_model import BaseModelConfig
from src.config.types import Directory

from .connection_configs import ConnectionsConfig
from .model_configs import ModelsConfig
from ..base_config import BaseConfig, BaseSettings


# class AgentSettings(BaseSettings):
# secret_key: int = Field(validation_alias="SECRET_KEY")
class AgentSettings(BaseSettings):
    default_llm_provider: Optional[str] = Field(validation_alias="DEFAULT_LLM_PROVIDER")


class AgentConfig(BaseConfig):
    # user set config
    name: str
    bio: List[str]
    traits: List[str]
    connections: ConnectionsConfig
    models: ModelsConfig
    agent_settings: AgentSettings = AgentSettings()  # type: ignore
    # default_model_provider: BaseModelConfig
    # agent_settings: AgentSettings = AgentSettings()

    username: Optional[str] = None
    _system_prompt: Optional[str] = None

    def set_default_model_provider(self, provider: str | None = None) -> None:
        def_provider: str
        if provider is None:
            providers = self.list_models()
            if len(providers) == 0:
                raise ValueError("No configured models found")
            def_provider = providers[0]
        else:
            def_provider = provider
        self.default_model_provider = self.get_model(def_provider)

    def list_connections(self) -> List[str]:
        return [
            key
            for key, value in self.connections.model_dump().items()
            if isinstance(value, dict) and len(value) > 0
        ]

    def invalid_connections(self) -> List[str]:
        return [
            key
            for key, value in self.connections.model_dump().items()
            if not isinstance(value, dict) or len(value) == 0
        ]

    def list_models(self) -> List[str]:
        return [
            key
            for key, value in self.models.model_dump().items()
            if isinstance(value, dict) and len(value) > 0
        ]

    def get_connection(self, connection_name: str) -> Any:
        connections = self.connections.__dict__
        connection: BaseConnectionConfig | None = connections.get(connection_name)
        if connection is None:
            raise ValueError(
                f"Connection {connection_name} not configured for agent {self.name}"
            )
        return connection

    def get_model(self, model_name: str) -> Any:
        models = self.models.__dict__
        model: BaseModelConfig | None = models.get(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not configured for agent {self.name}")
        return model

    def to_json(self) -> dict[str, Any]:
        return self.model_dump()

    def set_system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt


def get_agents(path: Directory) -> Dict[str, AgentConfig | ValidationError]:
    # iterate over all files in the directory
    # if the file is a supported config file, parse it. supports json and yaml
    # and add it to the agents dict
    agents: Dict[str, AgentConfig | ValidationError] = {}
    # check extension for either json or yaml
    for file in os.listdir(path):
        if file.endswith(".json"):
            # if parse_json returns None, skip this file
            result = parse_json(path / file)
        elif file.endswith(".yaml"):
            result = parse_yaml(path / file)
        else:
            continue
        if isinstance(result, AgentConfig):
            agents[result.name] = result
        elif isinstance(result, ValidationError):
            agents[file] = result
        else:
            raise result
    return agents


def parse_json(path: Path) -> AgentConfig | ValidationError:
    with open(path) as f:
        config = json.load(f)
    try:
        return AgentConfig(**config)
    except ValidationError as e:
        return e


def parse_yaml(path: Path) -> AgentConfig | ValidationError:
    with open(path) as f:
        config = yaml.safe_load(f)
    try:
        return AgentConfig(**config)
    except ValidationError as e:
        raise e
