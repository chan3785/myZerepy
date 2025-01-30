import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter

import logging
from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import EternalAIService
from src.lib import deep_pretty_print

logger = logging.getLogger(__name__)


class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )


class GenerateTextOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=True,
        type=TypeAdapter(AgentName).validate_python,
    )
    PROMPT = click.Option(
        ["--prompt", "-p"],
        required=True,
        type=str,
    )
    SYSTEM_PROMPT = click.Option(
        ["--system-prompt", "-s"],
        required=True,
        type=str,
    )
    MODEL = click.Option(
        ["--model", "-m"],
        required=False,
        type=str,
    )
    CHAIN_ID = click.Option(
        ["--chain-id", "-c"],
        required=False,
        type=str,
    )


class CheckModelOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=True,
        type=TypeAdapter(AgentName).validate_python,
    )
    MODEL = click.Option(
        ["--model", "-m"],
        required=True,
        type=str,
    )


class ListModelsOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=True,
        type=TypeAdapter(AgentName).validate_python,
    )


@CliController("eternalai")
class EternalAICliController:
    def __init__(self, eternal_service: EternalAIService):
        self.eternal_service = eternal_service

    @CliCommand("get-config")
    def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("eternalai")
            for key, value in cfgs.items():
                cfg_dict = self.eternal_service.get_cfg(value)
                logger.info(f"Config for {key}: {json.dumps(cfg_dict, indent=4)}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("eternalai")
            cfg_dict = self.eternal_service.get_cfg(cfg)
            logger.info(f"Config for {agent}: {json.dumps(cfg_dict, indent=4)}")

    @CliCommand("generate")
    async def generate_text(
        self,
        agent: GenerateTextOptions.AGENT,  # type: ignore
        prompt: GenerateTextOptions.PROMPT,  # type: ignore
        system_prompt: GenerateTextOptions.SYSTEM_PROMPT,  # type: ignore
        model: GenerateTextOptions.MODEL,  # type: ignore
        chain_id: GenerateTextOptions.CHAIN_ID,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("eternalai")
        res = await self.eternal_service.generate_text(
            cfg,
            prompt,
            system_prompt,
            model,
            chain_id,
        )
        logger.info(f"Generated text:\n{res}")

    @CliCommand("check-model")
    async def check_model(
        self,
        agent: CheckModelOptions.AGENT,  # type: ignore
        model: CheckModelOptions.MODEL,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("eternalai")
        res = await self.eternal_service.check_model(cfg, model)
        logger.info(f"Model {model} is {'available' if res else 'not available'}")

    @CliCommand("list-models")
    async def list_models(
        self,
        agent: ListModelsOptions.AGENT,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("eternalai")
        models = await self.eternal_service.list_models(cfg)
        if models:
            logger.info("\nAvailable fine-tuned models:")
            for i, model in enumerate(models, 1):
                logger.info(f"{i}. {model}")
        else:
            logger.info("No fine-tuned models available")