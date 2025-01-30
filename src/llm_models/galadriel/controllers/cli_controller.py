import json
import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from pydantic import TypeAdapter
from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..galadriel_service import GaladrielService
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
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    PROMPT = click.Argument(
        ["prompt"],
        required=True,
        type=str,
    )
    SYSTEM_PROMPT = click.Argument(
        ["system_prompt"],
        required=True,
        type=str,
    )
    MODEL = click.Option(
        ["--model", "-m"],
        required=False,
        type=str,
    )

class ModelOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    MODEL = click.Argument(
        ["model"],
        required=True,
        type=str,
    )

@CliController("galadriel")
class GaladrielCliController:
    def __init__(self, galadriel_service: GaladrielService):
        self.galadriel_service = galadriel_service

    @CliCommand("get-config")
    async def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        logger.info(f"Getting config for {agent}")
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("galadriel")
            for key, value in cfgs.items():
                cfg_dict = self.galadriel_service.get_cfg(value)
                logger.info(f"Config for {key}: {json.dumps(cfg_dict, indent=4)}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("galadriel")
            cfg_dict = self.galadriel_service.get_cfg(cfg)
            logger.info(f"Config for {agent}: {json.dumps(cfg_dict, indent=4)}")

    @CliCommand("generate-text")
    async def generate_text(
        self,
        prompt: GenerateTextOptions.PROMPT,  # type: ignore
        system_prompt: GenerateTextOptions.SYSTEM_PROMPT,  # type: ignore
        agent: GenerateTextOptions.AGENT,  # type: ignore
        model: GenerateTextOptions.MODEL,  # type: ignore
    ) -> None:
        logger.info(f"Generating text with agent {agent}")
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("galadriel")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("galadriel")
            
        res = self.galadriel_service.generate_text(cfg, prompt, system_prompt, model)
        logger.info(f"Generated text:\n{res}")

    @CliCommand("check-model")
    async def check_model(
        self,
        model: ModelOptions.MODEL,  # type: ignore
        agent: ModelOptions.AGENT,  # type: ignore
    ) -> None:
        logger.info(f"Checking model {model} availability")
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("galadriel")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("galadriel")
            
        res = self.galadriel_service.check_model(cfg, model)
        logger.info(f"Model {model} is {'available' if res else 'not available'}")

    @CliCommand("list-models")
    async def list_models(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        logger.info("Listing available models")
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("galadriel")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("galadriel")
            
        models = self.galadriel_service.list_models(cfg)
        logger.info("\nAvailable Models:")
        for i, model in enumerate(models, 1):
            logger.info(f"{i}. {model.id}")