import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from pydantic import TypeAdapter, PositiveInt
from src.config.zerepy_config import ZEREPY_CONFIG, AgentName
from ..twitter_service import TwitterService
import logging

logger = logging.getLogger(__name__)

class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        help="The agent to get the config for",
    )

class TimelineOptions:
    COUNT = click.Option(
        ["--count", "-c"],
        required=False,
        type=TypeAdapter(PositiveInt).validate_python,
        help="Number of tweets to retrieve",
    )
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

class TweetOptions:
    MESSAGE = click.Argument(
        ["message"],
        required=True,
        type=str,
    )
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

class ReplyOptions:
    TWEET_ID = click.Argument(
        ["tweet_id"],
        required=True,
        type=str,
    )
    MESSAGE = click.Argument(
        ["message"],
        required=True,
        type=str,
    )
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

class LikeOptions:
    TWEET_ID = click.Argument(
        ["tweet_id"],
        required=True,
        type=str,
    )
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )

@CliController("twitter")
class TwitterCliController:
    def __init__(self, twitter_service: TwitterService):
        self.twitter_service = twitter_service

    @CliCommand("get-config")
    async def get_config(self, agent: GetConfigOptions.AGENT) -> None:  # type: ignore
        logger.info(f"Getting config for {agent}")
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("twitter")
            for key, value in cfgs.items():
                logger.info(f"Config for {key}: {value.to_json()}")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("twitter")
            logger.info(f"Config for {agent}: {cfg.to_json()}")

    @CliCommand("read-timeline")
    async def read_timeline(
        self, 
        count: TimelineOptions.COUNT,  # type: ignore
        agent: TimelineOptions.AGENT,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("twitter")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("twitter")
        
        tweets = await self.twitter_service.read_timeline(cfg, count)
        for tweet in tweets:
            logger.info(f"Tweet from {tweet['author_username']}: {tweet['text']}")

    @CliCommand("post-tweet")
    async def post_tweet(
        self,
        message: TweetOptions.MESSAGE,  # type: ignore
        agent: TweetOptions.AGENT,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("twitter")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("twitter")
        
        result = await self.twitter_service.post_tweet(cfg, message)
        logger.info(f"Tweet posted successfully: {result['data']['id']}")

    @CliCommand("reply-to-tweet")
    async def reply_to_tweet(
        self,
        tweet_id: ReplyOptions.TWEET_ID,  # type: ignore
        message: ReplyOptions.MESSAGE,  # type: ignore
        agent: ReplyOptions.AGENT,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("twitter")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("twitter")
        
        result = await self.twitter_service.reply_to_tweet(cfg, tweet_id, message)
        logger.info(f"Reply posted successfully: {result['data']['id']}")

    @CliCommand("like-tweet")
    async def like_tweet(
        self,
        tweet_id: LikeOptions.TWEET_ID,  # type: ignore
        agent: LikeOptions.AGENT,  # type: ignore
    ) -> None:
        if agent is None:
            cfg = ZEREPY_CONFIG.get_default_agent().get_connection("twitter")
        else:
            cfg = ZEREPY_CONFIG.get_agent(agent).get_connection("twitter")
        
        result = await self.twitter_service.like_tweet(cfg, tweet_id)
        logger.info("Tweet liked successfully")