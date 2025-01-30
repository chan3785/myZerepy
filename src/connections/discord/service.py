import logging
import json
import requests
from typing import Any, Dict
from src.config.agent_config.connection_configs.discord import DiscordConfig

logger = logging.getLogger(__name__)


class DiscordService:
    def __init__(self):
        self.base_url = "https://discord.com/api/v10"

    ############### reads ###############
    def get_cfg(self, cfg: DiscordConfig) -> dict[str, Any]:
        return cfg.to_json()

    def list_channels(self, cfg: DiscordConfig, server_id: str) -> dict:
        """Lists all Discord channels under the server"""
        request_path = f"/guilds/{server_id}/channels"
        response = self._get_request(cfg, request_path)
        text_channels = self._filter_channels_for_type_text(response)
        formatted_response = self._format_channels(text_channels)
        logger.info(f"Retrieved {len(formatted_response)} channels")
        return formatted_response

    def read_messages(self, cfg: DiscordConfig, channel_id: str, count: int) -> dict:
        """Reading messages in a channel"""
        logger.debug("Reading messages")
        request_path = f"/channels/{channel_id}/messages?limit={count}"
        response = self._get_request(cfg, request_path)
        formatted_response = self._format_messages(response)
        logger.info(f"Retrieved {len(formatted_response)} messages")
        return formatted_response

    def read_mentioned_messages(
        self, cfg: DiscordConfig, channel_id: str, count: int
    ) -> dict:
        """Reads messages in a channel and filters for bot mentioned messages"""
        messages = self.read_messages(cfg, channel_id, count)
        mentioned_messages = self._filter_message_for_bot_mentions(cfg, messages)
        logger.info(f"Retrieved {len(mentioned_messages)} mentioned messages")
        return mentioned_messages

    ############### writes ###############
    def post_message(self, cfg: DiscordConfig, channel_id: str, message: str) -> dict:
        """Send a new message"""
        logger.debug("Sending a new message")
        request_path = f"/channels/{channel_id}/messages"
        payload = json.dumps({"content": f"{message}"})
        response = self._post_request(cfg, request_path, payload)
        formatted_response = self._format_posted_message(response)
        logger.info("Message posted successfully")
        return formatted_response

    def reply_to_message(
        self, cfg: DiscordConfig, channel_id: str, message_id: str, message: str
    ) -> dict:
        """Reply to a message"""
        logger.debug("Replying to a message")
        request_path = f"/channels/{channel_id}/messages"
        payload = json.dumps(
            {
                "content": f"{message}",
                "message_reference": {
                    "channel_id": f"{channel_id}",
                    "message_id": f"{message_id}",
                },
            }
        )
        response = self._post_request(cfg, request_path, payload)
        formatted_response = self._format_reply_message(response)
        logger.info("Reply message posted successfully")
        return formatted_response

    def react_to_message(
        self, cfg: DiscordConfig, channel_id: str, message_id: str, emoji_name: str
    ) -> None:
        """React to a message"""
        logger.debug("Reacting to a message")
        request_path = (
            f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji_name}/@me"
        )
        self._put_request(cfg, request_path)
        logger.info("Reacted to message successfully")

    ############### helpers ###############
    def _format_reply_message(self, reply_message: dict) -> dict:
        mentions = []
        for mention in reply_message["mentions"]:
            mentions.append({"id": mention["id"], "username": mention["username"]})
        return {
            "id": reply_message["id"],
            "channel_id": reply_message["channel_id"],
            "author": reply_message["author"]["username"],
            "content": reply_message["content"],
            "timestamp": reply_message["timestamp"],
            "mentions": mentions,
        }

    def _format_posted_message(self, posted_message: dict) -> dict:
        mentions = []
        for mention in posted_message["mentions"]:
            mentions.append({"id": mention["id"], "username": mention["username"]})
        return {
            "id": posted_message["id"],
            "channel_id": posted_message["channel_id"],
            "content": posted_message["content"],
            "timestamp": posted_message["timestamp"],
            "mentions": mentions,
        }

    def _format_messages(self, messages: dict) -> dict:
        formatted_messages = []
        for message in messages:
            mentions = []
            for mention in message["mentions"]:
                mentions.append({"id": mention["id"], "username": mention["username"]})
            formatted_message = {
                "id": message["id"],
                "channel_id": message["channel_id"],
                "author": message["author"]["username"],
                "message": message["content"],
                "timestamp": message["timestamp"],
                "mentions": mentions,
            }
            formatted_messages.append(formatted_message)
        return formatted_messages

    def _format_channels(self, channels: dict) -> dict:
        formatted_channels = []
        for channel in channels:
            formatted_channel = {
                "id": channel["id"],
                "type": channel["type"],
                "name": channel["name"],
                "server_id": channel["guild_id"],
            }
            formatted_channels.append(formatted_channel)
        return formatted_channels

    def _put_request(self, cfg: DiscordConfig, url_path: str) -> None:
        url = f"{self.base_url}{url_path}"
        headers = {
            "Accept": "application/json",
            "Authorization": cfg.get_auth_token(),
        }
        response = requests.request("PUT", url, headers=headers, data={})
        if response.status_code != 204:
            raise Exception(
                f"Failed to called PUT to Discord: {response.status_code} - {response.text}"
            )
        return

    def _post_request(self, cfg: DiscordConfig, url_path: str, payload: str) -> dict:
        url = f"{self.base_url}{url_path}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": cfg.get_auth_token(),
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Failed to call POST to Discord: {response.status_code} - {response.text}"
            )
        return json.loads(response.text)

    def _get_request(self, cfg: DiscordConfig, url_path: str) -> str:
        url = f"{self.base_url}{url_path}"
        headers = {
            "Accept": "application/json",
            "Authorization": cfg.get_auth_token(),
        }
        response = requests.request("GET", url, headers=headers, data={})
        if response.status_code != 200:
            raise Exception(
                f"Failed to call GET to Discord: {response.status_code} - {response.text}"
            )
        return json.loads(response.text)

    def _filter_channels_for_type_text(self, data):
        """Helper method to filter for only channels that are text channels"""
        filtered_data = []
        for item in data:
            if item["type"] == 0:
                filtered_data.append(item)
        return filtered_data

    def _filter_message_for_bot_mentions(self, cfg: DiscordConfig, data):
        """Helper method to filter for messages that mention the bot"""
        filtered_data = []
        for item in data:
            for mention in item["mentions"]:
                if mention["username"] == cfg.get_bot_username():
                    filtered_data.append(item)
        return filtered_data
