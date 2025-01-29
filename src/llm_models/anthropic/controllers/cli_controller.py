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
    AGENT = click.Argument(
        ["agent"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )


@CliController("anthropic")
class AnthropicCliController:
    def __init__(self, anthropic_service: AnthropicService):
        self.anthropic_service = anthropic_service

    @CliCommand("get-config")
    def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        res = self.anthropic_service.get_cfg(agent)
        res_str = deep_pretty_print(
            res, blacklisted_fields=["logger", "settings"], partial_match=True
        )
        logging.info(f"Result:\n{res_str}")

    @CliCommand("generate-text")
    def generate_text(self, prompt: str, system_prompt: str, model: str = None) -> None:
        res = self.anthropic_service.generate_text(prompt, system_prompt, model)
        logging.info(f"Generated text:\n{res}")

    @CliCommand("check-model")
    def check_model(self, model: str) -> None:
        res = self.anthropic_service.check_model(model)
        logging.info(f"Model {model} availability: {res}")

    @CliCommand("list-models")
    def list_models(self) -> None:
        self.anthropic_service.list_models()