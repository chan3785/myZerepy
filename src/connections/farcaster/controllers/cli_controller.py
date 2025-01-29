import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
import click
from pydantic import TypeAdapter
import logging

from ....config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import FarcasterService
from src.lib import deep_pretty_print

logger = logging.getLogger(__name__)


class GetConfigOptions:
    AGENT = click.Argument(
        ["agent"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

class TimelineOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    LIMIT = click.Option(
        ["--limit", "-l"],
        required=False,
        type=int,
    )

class PostCastOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    TEXT = click.Argument(["text"], type=str)
    CHANNEL = click.Option(
        ["--channel", "-c"],
        required=False,
        type=str,
    )

class GetLatestCastsOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    FID = click.Argument(["fid"], type=int)
    LIMIT = click.Option(
        ["--limit", "-l"],
        required=False,
        type=int,
    )

class LikeCastOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    CAST_HASH = click.Argument(["cast_hash"], type=str)

class ReplyCastOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    PARENT_FID = click.Argument(["parent_fid"], type=int)
    PARENT_HASH = click.Argument(["parent_hash"], type=str)
    TEXT = click.Argument(["text"], type=str)
    CHANNEL = click.Option(
        ["--channel", "-c"],
        required=False,
        type=str,
    )


@CliController("farcaster")
class FarcasterCliController:
    def __init__(self, farcaster_service: FarcasterService):
        self.farcaster_service = farcaster_service

    @CliCommand("get-config")
    def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        res = self.farcaster_service.get_cfg(agent)
        res_str = deep_pretty_print(
            res, blacklisted_fields=["logger", "settings"], partial_match=True
        )
        logging.info(f"Result:\n{res_str}")
    
    @CliCommand("read-timeline")
    async def read_timeline(self, agent: TimelineOptions.AGENT, limit: TimelineOptions.LIMIT) -> None:  # type: ignore
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("farcaster")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("farcaster")
        
        casts = self.farcaster_service.read_timeline(cfg, limit=limit)
        logger.info(deep_pretty_print(casts))

    @CliCommand("post-cast")
    async def post_cast(self, agent: PostCastOptions.AGENT, text: PostCastOptions.TEXT, 
                       channel: PostCastOptions.CHANNEL) -> None:  # type: ignore
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("farcaster")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("farcaster")
        
        result = self.farcaster_service.post_cast(cfg, text, channel_key=channel)
        logger.info(f"Cast posted: {result}")

    @CliCommand("get-latest-casts")
    async def get_latest_casts(self, agent: GetLatestCastsOptions.AGENT, fid: GetLatestCastsOptions.FID,
                              limit: GetLatestCastsOptions.LIMIT) -> None:  # type: ignore
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("farcaster")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("farcaster")
        
        casts = self.farcaster_service.get_latest_casts(cfg, fid, limit=limit)
        logger.info(deep_pretty_print(casts))

    @CliCommand("like-cast")
    async def like_cast(self, agent: LikeCastOptions.AGENT, cast_hash: LikeCastOptions.CAST_HASH) -> None:  # type: ignore
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("farcaster")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("farcaster")
        
        result = self.farcaster_service.like_cast(cfg, cast_hash)
        logger.info(f"Cast liked: {result}")

    @CliCommand("reply-to-cast")
    async def reply_to_cast(self, agent: ReplyCastOptions.AGENT, parent_fid: ReplyCastOptions.PARENT_FID,
                           parent_hash: ReplyCastOptions.PARENT_HASH, text: ReplyCastOptions.TEXT,
                           channel: ReplyCastOptions.CHANNEL) -> None:  # type: ignore
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("farcaster")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("farcaster")
        
        result = self.farcaster_service.reply_to_cast(cfg, parent_fid, parent_hash, text, channel_key=channel)
        logger.info(f"Reply posted: {result}")