import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController

from src.solana.solana_service import SolanaService
import logging
from solders.pubkey import Pubkey

# how do i change the color of the font for the logger?

logger = logging.getLogger(__name__)


class SolanaOptions:
    INPUT_AMOUNT = click.Option(
        ["-i", "--input-amount"],
        help="Amount to input",
        required=True,
        type=float,
    )
    AGENT = click.Option(
        ["-a", "--agent"],
        help="Agent to use",
        required=True,
        type=str,
    )
    TOKEN_ADDRESS = click.Option(
        ["-t", "--token-address"],
        help="SPL token mint address (optional)",
        required=False,
        type=str,
    )


@CliController("solana")
class SolanaCliController:
    def __init__(self, solana_service: SolanaService):
        self.solana_service = solana_service

    @CliCommand("health")
    def health(self, agent: SolanaOptions.AGENT) -> None:  # type: ignore
        res = self.solana_service.health(agent)
        logger.info(res)

    # configures
    # transfer
    # swap
    # balance
    @CliCommand("balance")
    async def balance(self, agent: SolanaOptions.AGENT, token_address: SolanaOptions.TOKEN_ADDRESS) -> None:  # type: ignore
        logger.debug(f"Getting balance for {token_address}")
        spl: Pubkey | None = Pubkey.from_string(token_address) if not None else None
        res = await self.solana_service.get_balance(agent, spl)
        logger.info(
            f"Result: {res}",
        )

    # stake
    @CliCommand("stake")
    def stake(
        self, agent: SolanaOptions.AGENT, input_amount: SolanaOptions.INPUT_AMOUNT  # type: ignore
    ) -> None:
        res = self.solana_service.stake(agent, input_amount)
        logger.info(res)

    # lend
    """ async def lend(
        self, agent: SolanaOptions.AGENT, input_amount: SolanaOptions.INPUT_AMOUNT
    ) -> None:
        res = await self.solana_service.lend(agent, input_amount)
        logger.info(res) """

    # request faucet
    # deploy token
    # get price

    # get tps
    # get token data by ticker
    # get token data by address
    # launch pump fun token
