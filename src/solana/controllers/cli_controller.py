import click
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from pydantic import TypeAdapter

from solders.pubkey import Pubkey

from src.config.agent_config.connection_configs.solana import SolanaConfig
from src.types import JupiterTokenData
from ..solana_service import SolanaService
import logging
from src.config.base_config import BASE_CONFIG, AgentName

# how do i change the color of the font for the logger?

logger = logging.getLogger(__name__)


class BalanceOptions:
    AGENT = click.Option(
        ["--agent", "-a"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
    )
    TOKEN_ADDRESS = click.Option(
        ["--token-address", "-t"],
        required=False,
        type=Pubkey.from_string,
    )
    SOLANA_ADDRESS = click.Argument(
        ["solana_address"],
        required=False,
        type=Pubkey.from_string,
    )


class PriceOptions:
    TOKEN_ADDRESS_OR_TICKER = click.Argument(
        ["token_address_or_ticker"],
        required=True,
        type=str,
    )


class TokenDataOptions:
    TOKEN_ADDRESS_OR_TICKER = click.Argument(
        ["token_address_or_ticker"],
        required=True,
        type=str,
    )


class TokenData:
    address: str
    symbol: str


class SolanaCommandOptions:
    AGENT = click.Option(
        ["-a", "--agent"],
        required=False,
        type=TypeAdapter(AgentName).validate_python,
        default=BASE_CONFIG.default_agent,
        help="The agent to use. Will use the default agent if not provided",
    )

    class Balance:
        TOKEN_ADDRESS = click.Option(
            ["--token-address"],
            required=False,
            type=str,
            help="The token address to get the balance for",
        )

    class Price:
        TOKEN_ADDRESS_OR_TICKER = click.Argument(
            ["token_address_or_ticker"],
            required=True,
            type=str,
        )

    class GetToken:
        TOKEN_ADDRESS_OR_TICKER = click.Argument(
            ["token_address_or_ticker"],
            required=True,
            type=str,
        )


@CliController("solana")
class SolanaCliController:
    def __init__(self, solana_service: SolanaService):
        self.solana_service = solana_service

    @CliCommand("balance")
    async def balance(self, solana_address: BalanceOptions.SOLANA_ADDRESS, agent: BalanceOptions.AGENT, token_address: BalanceOptions.TOKEN_ADDRESS) -> None:  # type: ignore
        logger.info(f"Getting balance for { agent}")
        if token_address is None:
            res = "SOL Balance:\n"
        else:
            if agent is None:
                raise Exception("Token address requires agent")
            res = f"Token Balance for {token_address}:\n"
        if agent is None:
            if solana_address is None:
                cfgs = BASE_CONFIG.get_configs_by_connection("solana")
                for key, value in cfgs.items():
                    balance_res = await self.solana_service.get_balance(
                        value, token_address
                    )
                    res += f"{key}: {balance_res}\n"
            else:
                cfg = list(BASE_CONFIG.get_configs_by_connection("solana").values())[0]
                balance_res = await self.solana_service.get_balance(cfg, solana_address)
                res += f"Balance for {solana_address}: {balance_res}\n"
        else:
            cfg = BASE_CONFIG.get_agent(agent).get_connection("solana")
            balance_res = await self.solana_service.get_balance(
                cfg, solana_address, token_address
            )
            res += f"Balance for {solana_address}: {balance_res}\n"

        if len(res) < 1:
            raise Exception("Result is none")
        logger.info(res)

    # get_price
    @CliCommand("price")
    async def price(
        self,
        token_address_or_ticker: PriceOptions.TOKEN_ADDRESS_OR_TICKER,  # type: ignore
    ) -> None:
        logger.info(f"Getting price for {token_address_or_ticker}")
        cfg = BASE_CONFIG.get_default_agent().get_connection("solana")
        try:
            token_address = Pubkey.from_string(token_address_or_ticker)
        except:
            ticker = token_address_or_ticker
            res = await self.solana_service.get_token_data_by_ticker(cfg, ticker)
            addy = res.get("address", None)
            if addy is None:
                logger.error(f"Token {ticker} not found")
                return
            token_address = Pubkey.from_string(addy)
        price = await self.solana_service.get_price(cfg, token_address)
        logger.info(price)

    # async def get_tps(self, cfg: SolanaConfig) -> float:
    @CliCommand("tps")
    async def tps(self) -> None:
        cfg = list(BASE_CONFIG.get_configs_by_connection("solana").values())[0]
        tps = await self.solana_service.get_tps(cfg)
        logger.info(tps)

    # async def get_token_data_by_ticker(
    @CliCommand("get-token-data")
    async def get_token_data(
        self, token_address_or_ticker: TokenDataOptions.TOKEN_ADDRESS_OR_TICKER  # type: ignore
    ) -> None:
        cfg = list(BASE_CONFIG.get_configs_by_connection("solana").values())[0]
        res = {}
        try:
            token_address = Pubkey.from_string(token_address_or_ticker)
            token_data = await self.solana_service.get_token_data_by_address(
                cfg, token_address
            )
            res = {
                "address": token_address,
                "symbol": token_data.symbol,
            }
        except:
            ticker = token_address_or_ticker
            data = await self.solana_service.get_token_data_by_ticker(cfg, ticker)
            data["symbol"] = token_address_or_ticker
            res = data
        logger.info(
            f"Token Data for {token_address_or_ticker}:\nAddress: {res['address']}\nSymbol: {res['symbol']}"
        )

    # async def transfer(
    # async def trade(
    # async def stake(self, cfg: SolanaConfig, amount: float) -> str:

    def _is_address(self, token_address_or_ticker: str) -> bool:
        try:
            Pubkey.from_string(token_address_or_ticker)
            return True
        except:
            return False
