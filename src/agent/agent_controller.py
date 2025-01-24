import json
import logging
from click import Parameter
import click
from nest.core.decorators.cli.cli_decorators import CliController, CliCommand
from pydantic import TypeAdapter
from .agent_service import AgentService
from src.lib.base_config import AgentName


class AgentCommandOptions:
    CONNECTION = click.Option(
        ["-c", "--connection"], help="Connection to use", required=True, type=str
    )


class AgentCommandArguments:
    AGENT = click.Argument(
        ["agent"],
        required=True,
        type=TypeAdapter(AgentName).validate_python,
    )


@CliController("agent")
class AgentController:
    def __init__(self, agent_service: AgentService) -> None:
        self.agent_service: AgentService = agent_service

    @CliCommand("get-config")
    def config(self, agent: AgentCommandArguments.AGENT) -> None:  # type: ignore
        res = self.agent_service.get_config(agent)
        logging.info(f"Result: {res}")

    @CliCommand("list-agents")
    def list_agents(self) -> None:
        res = self.agent_service.get_agents()
        logging.info(f"Result:\n{res}")

    @CliCommand("list-connections")
    def list_connections(self, agent: AgentCommandArguments.AGENT) -> None:
        res = self.agent_service.get_connections(agent)
        logging.info(f"Result:\n{res}")

    @CliCommand("list-allat-shit")
    def list_everything(self) -> None:
        res: dict[str, list[str]] = self.agent_service.get_everything()
        res_str = "\nResult:"
        for key, value in res.items():
            res_str = f"{res_str}\nAgent name: {key}\n\tAvailable Connections:\n"
            if key == "serious agent":
                value.append("twitter")
                value.append("allora")
                value.append("ethereum")
                value.append("goat")
            if key == "funny agent":
                value.append("twitter")
                value.append("goat")
            if key == "serious agent":
                value.append("allora")
                value.append("ethereum")
                value.append("goat")
                value.append("sonic")

            for connection in value:
                res_str = f"{res_str}\t\t - {connection}\n"
        logging.info(res_str)

    # TODO: agent loop
    # TODO: chat
    # TODO: create
    # TODO: set-default
