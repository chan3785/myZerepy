import os
from typing import Any, Dict, Optional
from pydantic import (
    Field,
    ValidationError,
)
from .base_config import BaseConfig, BaseSettings
from pydantic_core import ErrorDetails
from src.config.types import Directory
from src.config.agent_config import AgentConfig, get_agents
from pydantic import ValidationInfo, ValidatorFunctionWrapHandler
from typing import Annotated
from pydantic import WrapValidator
from typing_extensions import TypeAliasType


class ZerepyConfigException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ZerepySettings(BaseSettings):
    agents_dir: Directory = Field(validation_alias="AGENTS_DIR")
    default_agent: Optional[str] = Field(validation_alias="DEFAULT_AGENT")
    log_level: str = Field(validation_alias="LOG_LEVEL")


class ZerepyConfig(BaseConfig):
    version: str = "0.2.0"
    agents: Dict[str, AgentConfig] = {}
    # we need to change this. this is just a dev helper
    default_agent: Optional[str] = None
    zerepy_settings: ZerepySettings = ZerepySettings()  # type: ignore

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        get_agents_res = get_agents(self.zerepy_settings.agents_dir)
        for key, value in get_agents_res.items():
            if isinstance(value, AgentConfig):
                self.agents[key] = value
            else:
                error: ValidationError = value
                errors: list[ErrorDetails] = error.errors()
                for e in errors:
                    print(
                        f'{key} ERROR:\n{e.get("msg")}. Invalid Field(s): {".".join(map(str, e.get("loc", [])))}'
                    )
        def_agent = self.zerepy_settings.default_agent
        if def_agent is not None:
            if not self.is_agent_name(def_agent):
                raise ZerepyConfigException(
                    f"Agent {def_agent} not found. Agents: {self.agents.keys()}"
                )
            self.default_agent = def_agent

    def get_agents(self) -> list[str]:
        return list(self.agents.keys())

    def get_agent(self, agent_name: str) -> AgentConfig:
        res = self.agents.get(agent_name)
        if res is None:
            raise ZerepyConfigException(f"Agent {agent_name} not found")
        return res

    def is_agent_name(self, agent_name: str) -> bool:
        agents: Dict[str, AgentConfig] = self.__dict__["agents"]
        return agent_name in agents

    def set_default_agent(self, agent_name: str) -> None:
        if not self.is_agent_name(agent_name):
            raise ZerepyConfigException(f"Agent {agent_name} not found")
        self.default_agent = agent_name

    def get_configs_by_connection(self, connection: str) -> dict[str, Any]:
        configs: dict[str, Any] = {}
        for key, value in self.agents.items():
            try:
                conn = value.get_connection(connection)
                configs[key] = conn
            except:
                continue
        if len(configs) == 0:
            raise ZerepyConfigException(f"No agents have {connection} configured")
        return configs

    def get_default_agent(self) -> AgentConfig:
        if self.default_agent is None:
            raise ZerepyConfigException("No default agent set")
        return self.get_agent(self.default_agent)

    def get_class_methods(self) -> list[str]:
        return [
            attr
            for attr in dir(self)
            if callable(getattr(self, attr)) and not attr.startswith("__")
        ]


ZEREPY_CONFIG = ZerepyConfig()


def agent_name_validator(
    value: str, handler: ValidatorFunctionWrapHandler, _info: ValidationInfo
) -> str:
    if not ZEREPY_CONFIG.is_agent_name(value):
        raise ValueError(f"Agent {value} not found in config")
    return value


AgentName = TypeAliasType(
    "AgentName", Annotated[str, WrapValidator(agent_name_validator)]
)
