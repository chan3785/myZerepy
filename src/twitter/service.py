import json
import math
from typing import Any, Dict, List
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

    def get_latest_tweets(
        self, cfg: TwitterConfig, username: str | None, count: int | None = None
    ) -> list[Any]:
        """Get latest tweets for a user"""
        if username is None:
            username = cfg.twitter_settings.user_id
        if count is None:
            count = cfg.timeline_read_count
        logger.debug(f"Getting latest tweets for {username}, count: {count}")

        params = {
            "tweet.fields": "created_at,text",
            "max_results": min(count, 100),
            "query": f"from:{username} -is:retweet -is:reply",
        }

        response = cfg._make_request("get", f"tweets/search/recent", params=params)

        tweets: list[Any] = response.get("data", [])
        logger.debug(f"Retrieved {len(tweets)} tweets")
        return tweets

    def post_tweet(self, cfg: TwitterConfig, message: str) -> dict[str, Any]:
        """Post a new tweet"""
        logger.debug("Posting new tweet")
        cfg._validate_tweet_text(message)

        response = cfg._make_request("post", "tweets", json={"text": message})

        logger.info("Tweet posted successfully")
        return response

    def reply_to_tweet(
        self, cfg: TwitterConfig, tweet_id: str, message: str
    ) -> dict[str, Any]:
        """Reply to an existing tweet"""
        logger.debug(f"Replying to tweet {tweet_id}")
        cfg._validate_tweet_text(message, "Reply")

        response = cfg._make_request(
            "post",
            "tweets",
            json={"text": message, "reply": {"in_reply_to_tweet_id": tweet_id}},
        )

        logger.info("Reply posted successfully")
        return response

    def like_tweet(self, cfg: TwitterConfig, tweet_id: str) -> dict[str, Any]:
        """Like a tweet"""
        logger.debug(f"Liking tweet {tweet_id}")
        credentials = cfg.twitter_settings

        response = cfg._make_request(
            "post",
            f"users/{credentials.user_id}/likes",
            json={"tweet_id": tweet_id},
        )

        logger.info("Tweet liked successfully")
        return response

    def get_tweet_replies(
        self, cfg: TwitterConfig, tweet_id: str, count: int | None = None
    ) -> List[dict[str, Any]]:
        """Fetch replies to a specific tweet"""
        logger.debug(f"Fetching replies for tweet {tweet_id}, count: {count}")
        if count is None:
            count = cfg.own_tweet_replies_count
        params = {
            "query": f"conversation_id:{tweet_id} is:reply",
            "tweet.fields": "author_id,created_at,text",
            "max_results": min(count, 100),
        }

        response = cfg._make_request("get", "tweets/search/recent", params=params)
        replies: List[dict[str, Any]] = response.get("data", [])

        logger.info(f"Retrieved {len(replies)} replies")
        return replies
