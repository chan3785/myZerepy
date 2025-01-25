import os
from typing import Any, Dict, Optional
from pydantic import Field, BaseModel as PydanticBaseModel, TypeAdapter
from pydantic_settings import BaseSettings as PydanticBaseSettings
from src.config.types import Directory
from src.config.agent_config import AgentConfig, get_agents
from pydantic import ValidationInfo, ValidatorFunctionWrapHandler
from typing import Annotated
from pydantic import WrapValidator
from typing_extensions import TypeAliasType


class BaseConfigException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BaseSettings(PydanticBaseSettings):
    agents_dir: Directory = Field(validation_alias="AGENTS_DIR")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


class BaseConfig(PydanticBaseModel):
    version: str = "0.2.0"
    agents: Dict[str, AgentConfig] = {}
    # we need to change this. this is just a dev helper
    default_agent: Optional[str] = None
    base_settings: BaseSettings

    def __init__(self, **data: Any) -> None:
        settings = BaseSettings()
        data["base_settings"] = settings
        super().__init__(**data)
        self.agents = get_agents(settings.agents_dir)
        def_agent = os.getenv("DEFAULT_AGENT")
        if def_agent is not None:
            if not self.is_agent_name(def_agent):
                raise BaseConfigException(
                    f"Agent {def_agent} not found. Agents: {self.agents.keys()}"
                )
            self.default_agent = def_agent
        self.default_agent = def_agent

    def get_agents(self) -> list[str]:
        return list(self.agents.keys())

    def get_agent(self, agent_name: str) -> AgentConfig:
        res = self.agents.get(agent_name)
        if res is None:
            raise BaseConfigException(f"Agent {agent_name} not found")
        return res

    def is_agent_name(self, agent_name: str) -> bool:
        agents: Dict[str, AgentConfig] = self.__dict__["agents"]
        return agent_name in agents

    def set_default_agent(self, agent_name: str) -> None:
        if not self.is_agent_name(agent_name):
            raise BaseConfigException(f"Agent {agent_name} not found")
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
            raise BaseConfigException(f"No agents have {connection} configured")
        return configs

    def get_default_agent(self) -> AgentConfig:
        if self.default_agent is None:
            raise BaseConfigException("No default agent set")
        return self.get_agent(self.default_agent)


BASE_CONFIG = BaseConfig()


def agent_name_validator(
    value: str, handler: ValidatorFunctionWrapHandler, _info: ValidationInfo
) -> str:
    if not BASE_CONFIG.is_agent_name(value):
        raise ValueError(f"Agent {value} not found in config")
    return value


AgentName = TypeAliasType(
    "AgentName", Annotated[str, WrapValidator(agent_name_validator)]
)
