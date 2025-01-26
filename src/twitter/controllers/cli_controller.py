import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController

from src.twitter.twitter_service import TwitterService
import logging
from solders.pubkey import Pubkey
from src.config.base_config import BASE_CONFIG, AgentName

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

    # configures
    # transfer
    # swap
    # balance
    @CliCommand("balance")
    async def balance(self, agent: TwitterCommandArguments.AGENT, token_address: TwitterOptions.TOKEN_ADDRESS) -> None:  # type: ignore
        logger.debug(f"Getting balance for {token_address}")
        res = await self.twitter_service.get_balance(agent, token_address)
        logger.info(
            f"Result: {res}",
        )

    # stake
    @CliCommand("stake")
    def stake(
        self, agent: TwitterCommandArguments.AGENT, input_amount: TwitterOptions.INPUT_AMOUNT  # type: ignore
    ) -> None:
        res = self.twitter_service.stake(agent, input_amount)
        logger.info(res)

    # lend
    """ async def lend(
        self, agent: TwitterOptions.AGENT, input_amount: TwitterOptions.INPUT_AMOUNT
    ) -> None:
        res = await self.twitter_service.lend(agent, input_amount)
        logger.info(res) """

    # request faucet
    # deploy token
    # get price

    # get tps
    # get token data by ticker
    # get token data by address
    # launch pump fun token
