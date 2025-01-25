import json
import math
from typing import Any, Dict
from nest.core import Injectable

from src.config.agent_config import AgentConfig
from src.config.agent_config.connection_configs.twitter import TwitterConfig
from src.config.base_config import BASE_CONFIG
import logging

logger = logging.getLogger(__name__)


@Injectable
class TwitterService:
    cfg: TwitterConfig

    def handle(self, handler, **kwargs) -> Any:
        agent = kwargs.get("agent")
        if not agent or not BASE_CONFIG.is_agent_name(agent):
            raise Exception(f'Invalid agent: "{agent}"')
        self.cfg = self.get_cfg(agent)
        return handler(**kwargs)

    ############### misc ###############
    @staticmethod
    def get_cfg(agent: str) -> TwitterConfig:
        return BASE_CONFIG.get_agent(agent).connections.twitter

    # get-latest-tweets
    # post-tweet
    # read-timeline
    def read_timeline(self, count: int = None, **kwargs) -> list:
        """Read tweets from the user's timeline"""
        count = self.cfg.timeline_read_count

        logger.debug(f"Reading timeline, count: {count}")
        credentials = self.cfg.twitter_settings

        params = {
            "tweet.fields": "created_at,author_id,attachments",
            "expansions": "author_id",
            "user.fields": "name,username",
            "max_results": count,
        }

        response = self._make_request(
            "get",
            f"users/{credentials['TWITTER_USER_ID']}/timelines/reverse_chronological",
            params=params,
        )

        tweets = response.get("data", [])
        user_info = response.get("includes", {}).get("users", [])

        user_dict = {
            user["id"]: {"name": user["name"], "username": user["username"]}
            for user in user_info
        }

        for tweet in tweets:
            author_id = tweet["author_id"]
            author_info = user_dict.get(
                author_id, {"name": "Unknown", "username": "Unknown"}
            )
            tweet.update(
                {
                    "author_name": author_info["name"],
                    "author_username": author_info["username"],
                }
            )

        logger.debug(f"Retrieved {len(tweets)} tweets")
        return tweets

    # like-tweet
    # reply-to-tweet
    # get-tweet-replies
