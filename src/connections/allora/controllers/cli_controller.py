from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter
import logging
from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..allora_service import AlloraService

logger = logging.getLogger(__name__)

class GetInferenceOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    TOPIC_ID = click.Option(
        ["--topic-id", "-t"],
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

    @CliCommand("get-inference")
    async def get_inference(self, agent: GetInferenceOptions.AGENT, topic_id: GetInferenceOptions.TOPIC_ID) -> None:  # type: ignore
        logger.info(f"Getting inference for topic {topic_id}")
        cfg = ZEREPY_CONFIG.get_agent(agent or "default").get_connection("allora")
        result = await self.allora_service.get_inference(cfg, topic_id)
        logger.info(result)

    @CliCommand("list-topics") 
    async def list_topics(self, agent: ListTopicsOptions.AGENT) -> None:  # type: ignore
        logger.info("Listing available topics")
        cfg = ZEREPY_CONFIG.get_agent(agent or "default").get_connection("allora")
        topics = await self.allora_service.list_topics(cfg)
        logger.info(topics)