import json
import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from pydantic import TypeAdapter

import logging
from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..openai_service import OpenAIService

logger = logging.getLogger(__name__)

class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to get the config for",
    )

class GenerateTextOptions:
    PROMPT = click.Argument(["prompt"], required=True, type=str)
    SYSTEM_PROMPT = click.Argument(["system_prompt"], required=True, type=str)
    MODEL = click.Option(
        ["--model", "-m"],
        required=False,
        type=str,
        help="Model to use for generation",
    )
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to use",
    )

class CheckModelOptions:
    MODEL = click.Argument(["model"], required=True, type=str)
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to use",
    )

@CliController("openai")
class OpenAICliController:
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service

    @CliCommand("get-config")
    async def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        logger.info(f"Getting config for {agent}")
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("openai")
            for key, value in cfgs.items():
                cfg_dict = self.openai_service.get_cfg(value)
                logger.info(f"Config for {key}: {json.dumps(cfg_dict, indent=4)}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("openai")
            cfg_dict = self.openai_service.get_cfg(cfg)
            logger.info(f"Config for {agent}: {json.dumps(cfg_dict, indent=4)}")
        
    @CliCommand("generate-text")
    async def generate_text(
        self,
        prompt: GenerateTextOptions.PROMPT,  # type: ignore
        system_prompt: GenerateTextOptions.SYSTEM_PROMPT,  # type: ignore
        model: GenerateTextOptions.MODEL,  # type: ignore
        agent: GenerateTextOptions.AGENT,  # type: ignore
    ) -> None:
        logger.info(f"Generating text with model: {model}")
        cfg = ZEREPY_CONFIG.get_agent(agent if agent else "default").get_connection("openai")
        res = await self.openai_service.generate_text(cfg, prompt, system_prompt, model)
        logger.info(f"Generated text:\n{res}")
        
    @CliCommand("check-model")
    async def check_model(
        self,
        model: CheckModelOptions.MODEL,  # type: ignore
        agent: CheckModelOptions.AGENT,  # type: ignore
    ) -> None:
        logger.info(f"Checking model availability: {model}")
        cfg = ZEREPY_CONFIG.get_agent(agent if agent else "default").get_connection("openai")
        res = await self.openai_service.check_model(cfg, model)
        logger.info(f"Model {model} availability: {res}")
        
    @CliCommand("list-models")
    async def list_models(self) -> None:
        logger.info("Listing available models")
        cfg = ZEREPY_CONFIG.get_default_agent().get_connection("openai")
        await self.openai_service.list_models(cfg)