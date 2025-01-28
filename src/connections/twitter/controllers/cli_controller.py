import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from ..service import TwitterService
import logging
from src.config.zerepy_config import AgentName

# how do i change the color of the font for the logger?

logger = logging.getLogger(__name__)


class GetConfigOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=AgentName,
    )


@CliController("twitter")
class TwitterCliController:
    def __init__(self, twitter_service: TwitterService):
        self.twitter_service = twitter_service
