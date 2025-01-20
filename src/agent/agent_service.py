import os
from pathlib import Path
from typing import Any, Dict, List
from nest.core import Injectable

from src.agent.agent_config import AgentConfig

import logging

from src.constants import CONNECTION_CONFIGS
from src.lib.base_connection import BaseConnectionConfig
from src.solana.solana_config import SolanaConfig

logger = logging.getLogger(__name__)


@Injectable
class AgentService:
    loaded_agent: AgentConfig

    def load_agent(self, agent_name: str) -> None:
        self.loaded_agent = AgentConfig(agent_name)

    def get_config(self, agent_name: str) -> Dict[str, Any]:
        self.load_agent(agent_name)
        return self.loaded_agent.config_to_dict()

    def list_agents(self) -> List[str]:
        return [
            config
            for config in AgentConfig.configs()
            if AgentConfig.is_valid_config(config)
        ]

    def get_connections(self, agent_name: str) -> list[str]:
        self.load_agent(agent_name)
        connections: list[str] = []
        for conn_cfg in CONNECTION_CONFIGS:
            try:
                conn_cfg(agent_name)
                connections.append(conn_cfg.config_key())
            except Exception as e:
                pass
        return connections
