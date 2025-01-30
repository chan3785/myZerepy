import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter

import logging
from ....config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import HyperbolicService
from src.lib import deep_pretty_print

logger = logging.getLogger(__name__)

class GetConfigOptions:
    AGENT = click.Argument(
        ["agent"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

class GenerateTextOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to use for generation",
    )
    PROMPT = click.Argument(
        ["prompt"],
        required=True,
        type=str,
    )
    SYSTEM_PROMPT = click.Option(
        ["--system-prompt", "-s"],
        required=True,
        type=str,
        help="System prompt to guide the model",
    )
    MODEL = click.Option(
        ["--model", "-m"],
        required=False,
        type=str,
        help="Model to use for generation",
    )

class CheckModelOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to check the model for",
    )
    MODEL = click.Argument(
        ["model"],
        required=True,
        type=str,
    )

@CliController("hyperbolic")
class HyperbolicCliController:
    def __init__(self, hyperbolic_service: HyperbolicService):
        self.hyperbolic_service = hyperbolic_service

    @CliCommand("get-config")
    def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        res = self.hyperbolic_service.get_cfg(agent)
        res_str = deep_pretty_print(
            res, blacklisted_fields=["logger", "settings"], partial_match=True
        )
        logging.info(f"Result:\n{res_str}")

    @CliCommand("generate")
    async def generate_text(
        self,
        prompt: GenerateTextOptions.PROMPT,  # type: ignore
        system_prompt: GenerateTextOptions.SYSTEM_PROMPT,  # type: ignore
        agent: GenerateTextOptions.AGENT,  # type: ignore
        model: GenerateTextOptions.MODEL,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("hyperbolic")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("hyperbolic")

        res = await self.hyperbolic_service.generate_text(
            cfg,
            prompt,
            system_prompt,
            model
        )
        logging.info(f"Generated text:\n{res}")

    @CliCommand("check-model")
    async def check_model(
        self,
        model: CheckModelOptions.MODEL,  # type: ignore
        agent: CheckModelOptions.AGENT,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("hyperbolic")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("hyperbolic")

        res = await self.hyperbolic_service.check_model(cfg, model)
        logging.info(f"Model {model} available: {res}")

    @CliCommand("list-models")
    async def list_models(self) -> None:
        cfg = ZEREPY_CONFIG.get_default_agent().get_connection("hyperbolic")
        models = await self.hyperbolic_service.list_models(cfg)
        logging.info("\nAvailable Models:")
        for i, model_id in enumerate(models, start=1):
            logging.info(f"{i}. {model_id}")