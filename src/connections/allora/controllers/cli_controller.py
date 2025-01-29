import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter

import logging
from ....config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import AlloraService
from src.lib import deep_pretty_print

logger = logging.getLogger(__name__)

class GetConfigOptions:
    AGENT = click.Argument(
        ["agent"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

class GetInferenceOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    TOPIC_ID = click.Option(
        ["--topic-id"],
        required=True,
        type=int,
        help="Topic ID to get inference for"
    )

class ListTopicsOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

@CliController("allora")
class AlloraCliController:
    def __init__(self, allora_service: AlloraService):
        self.allora_service = allora_service

    @CliCommand("get-config")
    def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        res = self.allora_service.get_cfg(agent)
        res_str = deep_pretty_print(
            res, blacklisted_fields=["logger", "settings"], partial_match=True
        )
        logging.info(f"Result:\n{res_str}")

    @CliCommand("get-inference")
    async def get_inference(self, agent: GetInferenceOptions.AGENT, topic_id: GetInferenceOptions.TOPIC_ID) -> None:  # type: ignore
        logger.info(f"Getting inference for topic {topic_id}")
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("allora")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("allora")
        
        result = self.allora_service.get_inference(cfg, topic_id)
        logger.info(result)

    @CliCommand("list-topics")
    async def list_topics(self, agent: ListTopicsOptions.AGENT) -> None:  # type: ignore
        logger.info("Listing available topics")
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("allora")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("allora")
        
        topics = self.allora_service.list_topics(cfg)
        logger.info(topics)