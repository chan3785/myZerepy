import json
import logging
import os
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_core import ErrorDetails, ValidationError
from pydantic_settings import BaseSettings
from typing import Any, List, Dict, Optional

from dotenv import load_dotenv
import yaml  # type: ignore
from src.config.types import Directory

from .connection_configs import ConnectionsConfig
from .tasks import Tasks

load_dotenv()

logger = logging.getLogger(__name__)


# class AgentSettings(BaseSettings):
# secret_key: int = Field(validation_alias="SECRET_KEY")


class AgentConfig(BaseModel):
    name: str
    bio: List[str]
    traits: List[str]
    examples: List[str]
    example_accounts: List[str]
    loop_delay: int
    connections: ConnectionsConfig
    tasks: Tasks
    use_time_based_weights: bool
    time_based_multipliers: Dict[str, float]
    # agent_settings: AgentSettings = AgentSettings()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # filter out connections with empty values
        for key, value in self.connections.model_dump().items():
            if value is None or len(value) == 0:
                print(f"Connection {key} not configured for agent {self.name}")
                self.connections.__dict__.pop(key)

    def list_connections(self) -> List[str]:
        connections = []
        for key, value in self.connections.model_dump().items():
            if value is not None:
                connections.append(key)

        return connections

    def get_connection(self, connection_name: str) -> Any:
        connections = self.connections.__dict__
        connection = connections.get(connection_name)
        if connection is None:
            raise ValueError(
                f"Connection {connection_name} not configured for agent {self.name}"
            )
        return connection


def get_agents(path: Directory) -> Dict[str, AgentConfig]:
    # iterate over all files in the directory
    # if the file is a supported config file, parse it. supports json and yaml
    # and add it to the agents dict
    agents = {}
    # check extension for either json or yaml
    for file in os.listdir(path):
        if file.endswith(".json"):
            # if parse_json returns None, skip this file
            result = parse_json(path / file)
        elif file.endswith(".yaml"):
            result = parse_yaml(path / file)
        else:
            logger.debug(f"Skipping file {file} as it is not a supported file type")
            continue
        if isinstance(result, AgentConfig):
            agents[result.name] = result
        else:
            continue
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
