from typing import Any, List
from nest.core import Injectable


import logging

from src.config.agent_config import AgentConfig
from src.config.base_config import BASE_CONFIG, BaseConfig, AgentName

logger = logging.getLogger(__name__)


@Injectable
class AgentService:

    def get_config(self, agent_name: str) -> dict[str, Any]:
        return BASE_CONFIG.get_agent(agent_name).to_json()

    def get_agents(self) -> List[AgentName]:
        return list(BASE_CONFIG.agents.keys())

    def get_connections(self, agent_name: str) -> list[str]:
        return BASE_CONFIG.get_agent(agent_name).list_connections()

    # lists all agents and their connections
    def get_everything(self) -> dict[str, list[str]]:
        everything = {}
        for agent in BASE_CONFIG.agents:
            everything[agent] = BASE_CONFIG.agents[agent].list_connections()
        return everything
