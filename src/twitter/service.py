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

    # get-latest-tweets
    # post-tweet
    # read-timeline
    def read_timeline(self, cfg: TwitterConfig, count: int | None = None) -> list[Any]:
        """Read tweets from the user's timeline"""
        if count is None:
            count = cfg.timeline_read_count

        logger.debug(f"Reading timeline, count: {count}")
        credentials = cfg.twitter_settings

        params = {
            "tweet.fields": "created_at,author_id,attachments",
            "expansions": "author_id",
            "user.fields": "name,username",
            "max_results": count,
        }

        response = cfg._make_request(
            "get",
            f"users/{credentials.user_id}/timelines/reverse_chronological",
            params=params,
        )

        tweets: list[Any] = response.get("data", [])
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
