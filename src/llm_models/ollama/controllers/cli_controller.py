import json
import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from pydantic import TypeAdapter

from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from src.lib import deep_pretty_print
from ..service import OllamaService
import logging

logger = logging.getLogger(__name__)

class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to get the config for",
    )

class GenerateTextOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=True,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to use for generation",
    )
    PROMPT = click.Argument(
        ["prompt"],
        required=True,
        type=str,
    )
    SYSTEM_PROMPT = click.Option(
        ["--system", "-s"],
        required=False,
        type=str,
        default="You are a helpful AI assistant.",
        help="System prompt to guide the model",
    )

class TestConnectionOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to test connection for",
    )

@CliController("ollama")
class OllamaCliController:
    def __init__(self, ollama_service: OllamaService):
        self.ollama_service = ollama_service

    @CliCommand("get-config")
    async def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        logger.info(f"Getting config for {agent}")
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("ollama")
            for key, value in cfgs.items():
                cfg_dict = self.ollama_service.get_cfg(value)
                logger.info(f"Config for {key}: {json.dumps(cfg_dict, indent=4)}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("ollama")
            cfg_dict = self.ollama_service.get_cfg(cfg)
            logger.info(f"Config for {agent}: {json.dumps(cfg_dict, indent=4)}")

    @CliCommand("generate")
    async def generate_text(
        self,
        prompt: GenerateTextOptions.PROMPT,  # type: ignore
        agent: GenerateTextOptions.AGENT,  # type: ignore
        system: GenerateTextOptions.SYSTEM_PROMPT,  # type: ignore
    ) -> None:
        logger.info(f"Generating text with agent {agent}")
        cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("ollama")
        response = await self.ollama_service.generate_text(cfg, prompt, system)
        logger.info(f"Generated text:\n{response}")

    @CliCommand("test")
    async def test_connection(self, agent: TestConnectionOptions.AGENT) -> None:  # type: ignore
        logger.info(f"Testing connection for {agent}")
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("ollama")
            for key, value in cfgs.items():
                is_connected = await self.ollama_service.test_connection(value)
                status = "✅" if is_connected else "❌"
                logger.info(f"Connection test for {key}: {status}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("ollama")
            is_connected = await self.ollama_service.test_connection(cfg)
            status = "✅" if is_connected else "❌"
            logger.info(f"Connection test for {agent}: {status}")