import json
import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from pydantic import TypeAdapter
from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..service import DiscordService
import logging

logger = logging.getLogger(__name__)


class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to get the config for",
    )


class ChannelOptions:
    SERVER_ID = click.Option(
        ["--server-id", "-s"],
        required=False,
        type=str,
    )


class MessageOptions:
    CHANNEL_ID = click.Argument(
        ["channel_id"],
        required=True,
        type=str,
    )
    COUNT = click.Option(
        ["--count", "-c"],
        required=False,
        type=int,
    )


class PostMessageOptions:
    CHANNEL_ID = click.Argument(
        ["channel_id"],
        required=True,
        type=str,
    )
    MESSAGE = click.Argument(
        ["message"],
        required=True,
        type=str,
    )


class ReplyMessageOptions:
    CHANNEL_ID = click.Argument(
        ["channel_id"],
        required=True,
        type=str,
    )
    MESSAGE_ID = click.Argument(
        ["message_id"],
        required=True,
        type=str,
    )
    MESSAGE = click.Argument(
        ["message"],
        required=True,
        type=str,
    )


class ReactMessageOptions:
    CHANNEL_ID = click.Argument(
        ["channel_id"],
        required=True,
        type=str,
    )
    MESSAGE_ID = click.Argument(
        ["message_id"],
        required=True,
        type=str,
    )
    EMOJI = click.Option(
        ["--emoji", "-e"],
        required=False,
        type=str,
    )


@CliController("discord")
class DiscordCliController:
    def __init__(self, discord_service: DiscordService):
        self.discord_service = discord_service

    @CliCommand("get-config")
    async def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        logger.info(f"Getting config for {agent}")
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("discord")
            for key, value in cfgs.items():
                cfg_dict = self.discord_service.get_cfg(value)
                logger.info(f"Config for {key}: {json.dumps(cfg_dict, indent=4)}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("discord")
            cfg_dict = self.discord_service.get_cfg(cfg)
            logger.info(f"Config for {agent}: {json.dumps(cfg_dict, indent=4)}")

    @CliCommand("list-channels")
    async def list_channels(self, server_id: ChannelOptions.SERVER_ID) -> None:  # type: ignore
        if server_id is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("discord")
            server_id = cfg.server_id
        else:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("discord")
        channels = self.discord_service.list_channels(cfg, server_id)
        logger.info(f"Channels: {json.dumps(channels, indent=4)}")

    @CliCommand("read-messages")
    async def read_messages(
        self,
        channel_id: MessageOptions.CHANNEL_ID,  # type: ignore
        count: MessageOptions.COUNT,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_default_agent().get_connection("discord")
        if count is None:
            count = cfg.message_read_count
        messages = self.discord_service.read_messages(cfg, channel_id, count)
        logger.info(f"Messages: {json.dumps(messages, indent=4)}")

    @CliCommand("read-mentioned-messages")
    async def read_mentioned_messages(
        self,
        channel_id: MessageOptions.CHANNEL_ID,  # type: ignore
        count: MessageOptions.COUNT,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_default_agent().get_connection("discord")
        if count is None:
            count = cfg.message_read_count
        messages = self.discord_service.read_mentioned_messages(cfg, channel_id, count)
        logger.info(f"Mentioned messages: {json.dumps(messages, indent=4)}")

    @CliCommand("post-message")
    async def post_message(
        self,
        channel_id: PostMessageOptions.CHANNEL_ID,  # type: ignore
        message: PostMessageOptions.MESSAGE,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_default_agent().get_connection("discord")
        response = self.discord_service.post_message(cfg, channel_id, message)
        logger.info(f"Posted message: {json.dumps(response, indent=4)}")

    @CliCommand("reply-to-message")
    async def reply_to_message(
        self,
        channel_id: ReplyMessageOptions.CHANNEL_ID,  # type: ignore
        message_id: ReplyMessageOptions.MESSAGE_ID,  # type: ignore
        message: ReplyMessageOptions.MESSAGE,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_default_agent().get_connection("discord")
        response = self.discord_service.reply_to_message(
            cfg, channel_id, message_id, message
        )
        logger.info(f"Reply sent: {json.dumps(response, indent=4)}")

    @CliCommand("react-to-message")
    async def react_to_message(
        self,
        channel_id: ReactMessageOptions.CHANNEL_ID,  # type: ignore
        message_id: ReactMessageOptions.MESSAGE_ID,  # type: ignore
        emoji: ReactMessageOptions.EMOJI,  # type: ignore
    ) -> None:
        cfg = ZEREPY_CONFIG.get_default_agent().get_connection("discord")
        if emoji is None:
            emoji = cfg.message_emoji_name
        self.discord_service.react_to_message(cfg, channel_id, message_id, emoji)
        logger.info("Reaction added successfully")
