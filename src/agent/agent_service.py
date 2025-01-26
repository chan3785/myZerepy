from typing import Any, List
from nest.core import Injectable


import logging

from src.config.agent_config import AgentConfig
from src.config.base_config import BASE_CONFIG, BaseConfig, AgentName
from src.twitter.service import TwitterService

logger = logging.getLogger(__name__)


@Injectable
class AgentService:
    def __init__(self, twitter_service: TwitterService):
        self.twitter_service = twitter_service

    def _construct_system_prompt(self, cfg: AgentConfig) -> str:
        """Construct the system prompt from agent configuration"""
        twitter_config = cfg.get_connection("twitter")
        if cfg._system_prompt is None:
            prompt_parts = []
            prompt_parts.extend(cfg.bio)

            if cfg.traits:
                prompt_parts.append("\nYour key traits are:")
                prompt_parts.extend(f"- {trait}" for trait in cfg.traits)

            if cfg.examples or cfg.example_accounts:
                prompt_parts.append(
                    "\nHere are some examples of your style (Please avoid repeating any of these):"
                )
                if cfg.examples:
                    prompt_parts.extend(f"- {example}" for example in cfg.examples)

                if cfg.example_accounts:
                    for example_account in cfg.example_accounts:
                        tweets = self.twitter_service.get_latest_tweets(
                            twitter_config, example_account
                        )
                        if tweets:
                            prompt_parts.extend(
                                f"- {tweet['text']}" for tweet in tweets
                            )
            prompt = "\n".join(prompt_parts)
            cfg.set_system_prompt(prompt)

        return prompt

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
