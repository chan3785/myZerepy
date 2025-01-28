from typing import Any, List
from nest.core import Injectable


import logging

from src.config.agent_config import AgentConfig
from src.config.zerepy_config import ZEREPY_CONFIG, ZerepyConfig, AgentName
from src.connections.twitter.service import TwitterService

logger = logging.getLogger(__name__)


@Injectable
class AgentService:
    def __init__(self, twitter_service: TwitterService):
        self.twitter_service = twitter_service

    def get_config(self, agent_name: str) -> dict[str, Any]:
        return ZEREPY_CONFIG.get_agent(agent_name).to_json()

    def get_agents(self) -> List[AgentName]:
        return list(ZEREPY_CONFIG.agents.keys())

    def get_connections(self, agent_name: str) -> list[str]:
        return ZEREPY_CONFIG.get_agent(agent_name).list_connections()

    def get_models(self, agent_name: str) -> list[str]:
        return ZEREPY_CONFIG.get_agent(agent_name).list_models()

    # lists all agents and their connections
    def get_everything(self) -> dict[str, dict[str, list[str]]]:
        everything: dict[str, dict[str, list[str]]] = {}
        agents = ZEREPY_CONFIG.get_agents()
        for a in agents:
            agent = ZEREPY_CONFIG.get_agent(a)
            connections = agent.list_connections()
            models = agent.list_models()
            everything[agent.name] = {"connections": connections, "models": models}
        return everything
