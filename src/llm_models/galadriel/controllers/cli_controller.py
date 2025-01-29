import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter

import logging
from ....config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import GaladrielService
from src.lib import deep_pretty_print

logger = logging.getLogger(__name__)


class GetConfigOptions:
    AGENT = click.Argument(
        ["agent"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

class GenerateTextOptions:
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

@CliController("galadriel")
class GaladrielCliController:
    def __init__(self, galadriel_service: GaladrielService):
        self.galadriel_service = galadriel_service

    @CliCommand("get-config")
    def get_config(self, agent: GetConfigOptions.AGENT) -> None: 
        res = self.galadriel_service.get_cfg(agent)
        res_str = deep_pretty_print(
            res, blacklisted_fields=["logger", "settings"], partial_match=True
        )
        logging.info(f"Result:\n{res_str}")

    @CliCommand("generate-text")
    def generate_text(
        self,
        prompt: GenerateTextOptions.PROMPT,
        system_prompt: GenerateTextOptions.SYSTEM_PROMPT,
        model: GenerateTextOptions.MODEL,
        agent: GetConfigOptions.AGENT,
    ) -> None:
        res = self.galadriel_service.generate_text(agent, prompt, system_prompt, model)
        logging.info(f"Generated Text:\n{res}")
