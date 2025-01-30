import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter

import logging
from ....config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import AnthropicService
from src.lib import deep_pretty_print

logger = logging.getLogger(__name__)


class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )


class GenerateTextOptions:
    PROMPT = click.Argument(["prompt"], required=True, type=str)
    SYSTEM_PROMPT = click.Argument(["system_prompt"], required=True, type=str)
    MODEL = click.Option(["--model", "-m"], required=False, type=str)
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )


class ModelOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    MODEL = click.Argument(["model"], required=True, type=str)


@CliController("anthropic")
class AnthropicCliController:
    def __init__(self, anthropic_service: AnthropicService):
        self.anthropic_service = anthropic_service

    @CliCommand("get-config")
    async def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        logger.info(f"Getting config for {agent}")
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("anthropic")
            for key, value in cfgs.items():
                cfg_dict = self.anthropic_service.get_cfg(value)
                logger.info(f"Config for {key}: {json.dumps(cfg_dict, indent=4)}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("anthropic")
            cfg_dict = self.anthropic_service.get_cfg(cfg)
            logger.info(f"Config for {agent}: {json.dumps(cfg_dict, indent=4)}")

    @CliCommand("generate-text")
    async def generate_text(
        self,
        prompt: GenerateTextOptions.PROMPT,  # type: ignore
        system_prompt: GenerateTextOptions.SYSTEM_PROMPT,  # type: ignore
        model: GenerateTextOptions.MODEL,  # type: ignore
        agent: GenerateTextOptions.AGENT,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("anthropic")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("anthropic")
        res = self.anthropic_service.generate_text(cfg, prompt, system_prompt, model)
        logger.info(f"Generated text:\n{res}")

    @CliCommand("check-model")
    async def check_model(
        self,
        model: ModelOptions.MODEL,  # type: ignore
        agent: ModelOptions.AGENT,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("anthropic")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("anthropic")
        res = self.anthropic_service.check_model(cfg, model)
        logger.info(f"Model {model} availability: {res}")

    @CliCommand("list-models")
    async def list_models(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("anthropic")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("anthropic")
        self.anthropic_service.list_models(cfg)