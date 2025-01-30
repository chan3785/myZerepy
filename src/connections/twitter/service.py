from typing import Any, Dict, List
from nest.core import Injectable
from src.config.agent_config.connection_configs.twitter import TwitterConfig
import logging

logger = logging.getLogger(__name__)

@Injectable
class TwitterService:
    def get_cfg(self, cfg: TwitterConfig) -> dict[str, Any]:
        return cfg.to_json()

    async def read_timeline(self, cfg: TwitterConfig, count: int | None = None) -> List[Dict[str, Any]]:
        """Read tweets from the user's timeline"""
        if count is None:
            count = cfg.timeline_read_count

        logger.debug(f"Reading timeline, count: {count}")
        params = {
            "tweet.fields": "created_at,author_id,attachments",
            "expansions": "author_id",
            "user.fields": "name,username",
            "max_results": count,
        }

        response = await cfg.make_request(
            "get",
            f"users/{cfg.twitter_settings.user_id}/timelines/reverse_chronological",
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
            tweet.update({
                "author_name": author_info["name"],
                "author_username": author_info["username"],
            })

        logger.debug(f"Retrieved {len(tweets)} tweets")
        return tweets

    async def post_tweet(self, cfg: TwitterConfig, message: str) -> Dict[str, Any]:
        """Post a new tweet"""
        logger.debug("Posting new tweet")
        cfg.validate_tweet_text(message)

        response = await cfg.make_request(
            "post", 
            "tweets", 
            json={"text": message}
        )

        logger.info("Tweet posted successfully")
        return response

    async def reply_to_tweet(
        self, 
        cfg: TwitterConfig, 
        tweet_id: str, 
        message: str
    ) -> Dict[str, Any]:
        """Reply to an existing tweet"""
        logger.debug(f"Replying to tweet {tweet_id}")
        cfg.validate_tweet_text(message, "Reply")

        response = await cfg.make_request(
            "post",
            "tweets",
            json={
                "text": message,
                "reply": {
                    "in_reply_to_tweet_id": tweet_id
                }
            }
        )

        logger.info("Reply posted successfully")
        return response

    async def like_tweet(self, cfg: TwitterConfig, tweet_id: str) -> Dict[str, Any]:
        """Like a tweet"""
        logger.debug(f"Liking tweet {tweet_id}")
        
        response = await cfg.make_request(
            "post",
            f"users/{cfg.twitter_settings.user_id}/likes",
            json={"tweet_id": tweet_id}
        )

        logger.info("Tweet liked successfully")
        return response

    async def get_tweet_replies(
        self, 
        cfg: TwitterConfig, 
        tweet_id: str, 
        count: int | None = None
    ) -> List[Dict[str, Any]]:
        """Fetch replies to a specific tweet"""
        logger.debug(f"Fetching replies for tweet {tweet_id}, count: {count}")
        
        if count is None:
            count = cfg.timeline_read_count

        params = {
            "query": f"conversation_id:{tweet_id} is:reply",
            "tweet.fields": "author_id,created_at,text",
            "max_results": min(count, 100)
        }

        response = await cfg.make_request("get", "tweets/search/recent", params=params)
        replies = response.get("data", [])

        logger.info(f"Retrieved {len(replies)} replies")
        return replies