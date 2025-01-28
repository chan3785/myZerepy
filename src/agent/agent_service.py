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

    # lists all agents and their connections
    def get_everything(self) -> dict[str, list[str]]:
        everything = {}
        for agent in ZEREPY_CONFIG.agents:
            everything[agent] = ZEREPY_CONFIG.agents[agent].list_connections()
        return everything
