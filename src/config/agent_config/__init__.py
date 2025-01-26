import json
import logging
import os
from pathlib import Path
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt
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
    # user set config
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

    # system set config
    model_provider: Optional[str] = None
    username: Optional[str] = None
    _system_prompt: Optional[str] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # filter out connections with empty values
        for key, value in self.connections.model_dump().items():
            if value is None or len(value) == 0:
                print(f"Connection {key} not configured for agent {self.name}")
                self.connections.__dict__.pop(key)

    def list_connections(self, is_llm_provider: bool | None = None) -> List[str]:
        connections = []
        for key, value in self.connections.model_dump().items():
            if is_llm_provider is None:
                if value is not None:
                    connections.append(key)
            else:
                if value is not None and getattr(
                    value, "is_llm_provider", lambda: is_llm_provider  # type: ignore
                ):
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

    def prompt_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text using the configured LLM provider"""
        system_prompt = system_prompt or self._construct_system_prompt()

        return self.connection_manager.perform_action(
            connection_name=self.model_provider,
            action_name="generate-text",
            params=[prompt, system_prompt],
        )

    def to_json(self) -> dict[str, Any]:
        return self.model_dump()

    def _setup_llm_provider(self) -> None:
        # Get first available LLM provider and its model
        llm_providers = self.list_connections(is_llm_provider=False)
        if not llm_providers:
            raise ValueError("No configured LLM provider found")
        self.model_provider = llm_providers[0]

        # Load Twitter username for self-reply detection if Twitter tasks exist
        if any("tweet" in task for task, weight in self.tasks.model_dump().items()):
            load_dotenv()
            self.username = os.getenv("TWITTER_USERNAME", "").lower()
            if not self.username:
                logger.warning(
                    "Twitter username not found, some Twitter functionalities may be limited"
                )

    def _adjust_weights_for_time(
        self, current_hour: PositiveFloat, task_weights: list[PositiveFloat]
    ) -> list[PositiveFloat]:
        weights = task_weights.copy()

        # Reduce tweet frequency during night hours (1 AM - 5 AM)
        if 1 <= current_hour <= 5:
            weights = [
                (
                    weight
                    * self.time_based_multipliers.get("tweet_night_multiplier", 0.4)
                    if task == "post-tweet"
                    else weight
                )
                for task, weight in self.tasks.model_dump().items()
            ]

        # Increase engagement frequency during day hours (8 AM - 8 PM) (peak hours?🤔)
        if 8 <= current_hour <= 20:
            weights = [
                (
                    weight
                    * self.time_based_multipliers.get("engagement_day_multiplier", 1.5)
                    if task in ("reply-to-tweet", "like-tweet")
                    else weight
                )
                for task, weight in self.tasks.model_dump().items()
            ]

        return weights

    def set_system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt


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
