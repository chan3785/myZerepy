import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter

import logging
from ....config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import GoatService
from src.lib import deep_pretty_print

# how do i change the color of the font for the logger?

logger = logging.getLogger(__name__)


class GetConfigOptions:
    AGENT = click.Argument(
        ["agent"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )


@CliController("goat")
class GoatCliController:
    def __init__(self, solana_service: GoatService):
        self.solana_service = solana_service

    @CliCommand("get-config")
    def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        res = self.solana_service.get_cfg(agent)
        res_str = deep_pretty_print(
            res, blacklisted_fields=["logger", "settings"], partial_match=True
        )
        logging.info(f"Result:\n{res_str}")
import json
import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from pydantic import TypeAdapter

import logging
from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from src.lib import deep_pretty_print
from ..goat_service import GoatService

logger = logging.getLogger(__name__)

class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to get the config for",
    )

class ExecuteToolOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=True,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to execute the tool for",
    )
    TOOL_NAME = click.Argument(
        ["tool_name"],
        type=str,
    )
    PARAMS = click.Argument(
        ["params"],
        type=str,
    )

class ListToolsOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=True,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to list tools for",
    )

@CliController("goat")
class GoatCliController:
    def __init__(self, goat_service: GoatService):
        self.goat_service = goat_service

    @CliCommand("get-config")
    async def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        """Get GOAT configuration for an agent"""
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("goat")
            for key, value in cfgs.items():
                cfg_dict = self.goat_service.get_cfg(value)
                logger.info(f"Config for {key}:")
                logger.info(deep_pretty_print(cfg_dict, blacklisted_fields=["logger", "settings"], partial_match=True))
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("goat")
            cfg_dict = self.goat_service.get_cfg(cfg)
            logger.info(f"Config for {agent}:")
            logger.info(deep_pretty_print(cfg_dict, blacklisted_fields=["logger", "settings"], partial_match=True))

    @CliCommand("list-tools")
    async def list_tools(self, agent: ListToolsOptions.AGENT) -> None:  # type: ignore
        """List available GOAT tools for an agent"""
        cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("goat")
        tools = self.goat_service.get_tools(cfg)
        
        logger.info(f"\nAvailable tools for {agent}:")
        for tool in tools:
            logger.info(f"\n{tool.name}: {tool.description}")
            logger.info("Parameters:")
            for field_name, field in tool.parameters.model_fields.items():
                required = "required" if field.is_required else "optional"
                logger.info(f"  - {field_name}: {field.description} ({required})")

    @CliCommand("execute-tool")
    async def execute_tool(
        self,
        agent: ExecuteToolOptions.AGENT,  # type: ignore
        tool_name: ExecuteToolOptions.TOOL_NAME,  # type: ignore
        params: ExecuteToolOptions.PARAMS,  # type: ignore
    ) -> None:
        """Execute a GOAT tool with parameters"""
        cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("goat")
        
        try:
            params_dict = json.loads(params)
        except json.JSONDecodeError:
            logger.error("Invalid JSON parameters format")
            return

        try:
            result = self.goat_service.execute_tool(cfg, tool_name, params_dict)
            logger.info(f"\nTool execution result:")
            logger.info(deep_pretty_print(result))
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")