import logging
import os
import requests
import asyncio
from typing import Dict, Any, Optional, cast
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair  # type: ignore
from jupiter_python_sdk.jupiter import Jupiter

from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.types import JupiterTokenData
from src.types.connections import SolanaConfig
from src.types.config import BaseConnectionConfig
from src.constants import LAMPORTS_PER_SOL, SPL_TOKENS
from src.helpers.solana.pumpfun import PumpfunTokenManager
from src.helpers.solana.faucet import FaucetManager
from src.helpers.solana.lend import AssetLender
from src.helpers.solana.stake import StakeManager
from src.helpers.solana.trade import TradeManager
from src.helpers.solana.token_deploy import TokenDeploymentManager
from src.helpers.solana.performance import SolanaPerformanceTracker
from src.helpers.solana.transfer import SolanaTransferHelper
from src.helpers.solana.read import SolanaReadHelper


from dotenv import load_dotenv, set_key

from jupiter_python_sdk.jupiter import Jupiter

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from solders.keypair import Keypair  # type: ignore


logger = logging.getLogger("connections.solana_connection")


class SolanaConnectionError(Exception):
    """Base exception for Solana connection errors"""

    pass


class SolanaConfigurationError(SolanaConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class SolanaConnection(BaseConnection):
    _client: Optional[AsyncClient]
    
    _client: Optional[AsyncClient]
    _wallet: Optional[Keypair]
    _jupiter: Optional[Jupiter]
    
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing Solana connection...")
        # Validate config before passing to super
        validated_config = SolanaConfig(**config)
        super().__init__(validated_config)
        self._client = None
        self._wallet = None
        self._jupiter = None

    @property
    def is_llm_provider(self) -> bool:
        return False

    def _get_connection_async(self) -> AsyncClient:
        if not self._client:
            self._client = AsyncClient(cast(SolanaConfig, self.config).rpc)
        return self._client

    _wallet: Optional[Keypair]
    
    def _get_wallet(self) -> Keypair:
        if not self._wallet:
            creds = self._get_credentials()
            self._wallet = Keypair.from_base58_string(creds["SOLANA_PRIVATE_KEY"])
        return self._wallet

    def _get_credentials(self) -> Dict[str, str]:
        """Get Solana credentials from environment with validation"""
        logger.debug("Retrieving Solana Credentials")
        load_dotenv()
        required_vars = {"SOLANA_PRIVATE_KEY": "solana wallet private key"}
        credentials = {}
        missing = []

        for env_var, description in required_vars.items():
            value = os.getenv(env_var)
            if not value:
                missing.append(description)
            credentials[env_var] = value

        if missing:
            error_msg = f"Missing Solana credentials: {', '.join(missing)}"
            raise SolanaConfigurationError(error_msg)

        # Validate the private key format
        Keypair.from_base58_string(credentials["SOLANA_PRIVATE_KEY"])
        logger.debug("All required credentials found")
        return credentials

    _jupiter: Optional[Jupiter]
    
    def _get_jupiter(self, keypair: Keypair, async_client: AsyncClient) -> Jupiter:
        if not self._jupiter:
            self._jupiter = Jupiter(
                async_client=async_client,
                keypair=keypair,
                quote_api_url="https://quote-api.jup.ag/v6/quote?",
                swap_api_url="https://quote-api.jup.ag/v6/swap",
                open_order_api_url="https://jup.ag/api/limit/v1/createOrder",
                cancel_orders_api_url="https://jup.ag/api/limit/v1/cancelOrders",
                query_open_orders_api_url="https://jup.ag/api/limit/v1/openOrders?wallet=",
                query_order_history_api_url="https://jup.ag/api/limit/v1/orderHistory",
                query_trade_history_api_url="https://jup.ag/api/limit/v1/tradeHistory",
            )
        return self._jupiter

    def validate_config(self, config: Dict[str, Any]) -> BaseConnectionConfig:
        """Validate Solana configuration from JSON and convert to Pydantic model"""
        try:
            # Convert dict config to Pydantic model
            validated_config = SolanaConfig(**config)
            return validated_config
        except Exception as e:
            raise ValueError(f"Invalid Solana configuration: {str(e)}")

    def register_actions(self) -> None:
        """Register available Solana actions"""
        self.actions = {
            "transfer": Action(
                name="transfer",
                parameters=[
                    ActionParameter("to_address", True, str, "Destination address"),
                    ActionParameter("amount", True, float, "Amount to transfer"),
                    ActionParameter(
                        "token_mint",
                        False,
                        str,
                        "Token mint address (optional for SOL)",
                    ),
                ],
                description="Transfer SOL or SPL tokens",
            ),
            "trade": Action(
                name="trade",
                parameters=[
                    ActionParameter(
                        "output_mint", True, str, "Output token mint address"
                    ),
                    ActionParameter("input_amount", True, float, "Input amount"),
                    ActionParameter(
                        "input_mint", False, str, "Input token mint (optional for SOL)"
                    ),
                    ActionParameter(
                        "slippage_bps", False, int, "Slippage in basis points"
                    ),
                ],
                description="Swap tokens using Jupiter",
            ),
            "get-balance": Action(
                name="get-balance",
                parameters=[
                    ActionParameter(
                        "token_address",
                        False,
                        str,
                        "Token mint address (optional for SOL)",
                    )
                ],
                description="Check SOL or token balance",
            ),
            "stake": Action(
                name="stake",
                parameters=[
                    ActionParameter("amount", True, float, "Amount of SOL to stake")
                ],
                description="Stake SOL",
            ),
            "lend-assets": Action(
                name="lend-assets",
                parameters=[ActionParameter("amount", True, float, "Amount to lend")],
                description="Lend assets",
            ),
            "request-faucet": Action(
                name="request-faucet",
                parameters=[],
                description="Request funds from faucet for testing",
            ),
            "deploy-token": Action(
                name="deploy-token",
                parameters=[
                    ActionParameter(
                        "decimals", False, int, "Token decimals (default 9)"
                    )
                ],
                description="Deploy a new token",
            ),
            "fetch-price": Action(
                name="fetch-price",
                parameters=[
                    ActionParameter(
                        "token_id", True, str, "Token ID to fetch price for"
                    )
                ],
                description="Get token price",
            ),
            "get-tps": Action(
                name="get-tps", parameters=[], description="Get current Solana TPS"
            ),
            "get-token-by-ticker": Action(
                name="get-token-by-ticker",
                parameters=[
                    ActionParameter("ticker", True, str, "Token ticker symbol")
                ],
                description="Get token data by ticker symbol",
            ),
            "get-token-by-address": Action(
                name="get-token-by-address",
                parameters=[ActionParameter("mint", True, str, "Token mint address")],
                description="Get token data by mint address",
            ),
            "launch-pump-token": Action(
                name="launch-pump-token",
                parameters=[
                    ActionParameter("token_name", True, str, "Name of the token"),
                    ActionParameter("token_ticker", True, str, "Token ticker symbol"),
                    ActionParameter("description", True, str, "Token description"),
                    ActionParameter("image_url", True, str, "Token image URL"),
                    ActionParameter("options", False, dict, "Additional token options"),
                ],
                description="Launch a Pump & Fun token",
            ),
        }

    def configure(self) -> bool:
        """Sets up Solana credentials"""
        logger.info("\n🔑 SOLANA CREDENTIALS SETUP")

        if self.is_configured():
            logger.info("\nSolana is already configured.")
            response = input("Do you want to reconfigure? (y/n): ")
            if response.lower() != "y":
                return True

        logger.info("\n📝 To get your Solana private key:")
        logger.info("1. Export your private key from your wallet")
        logger.info("2. Make sure it's in base58 format")
        logger.info("3. Never share this key with anyone")

        private_key = input("\nEnter your Solana private key: ")

        try:
            # Validate the private key format by attempting to create a keypair
            Keypair.from_base58_string(private_key)

            if not os.path.exists(".env"):
                with open(".env", "w") as f:
                    f.write("")

            set_key(".env", "SOLANA_PRIVATE_KEY", private_key)
            load_dotenv(override=True)

            logger.info("\n✅ Solana configuration successfully saved!")
            logger.info("Your private key has been stored in the .env file.")
            return True

        except Exception as e:
            logger.error(f"\n❌ Configuration failed: {e}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        """Check if Solana credentials are configured and valid"""
        try:
            # First check if credentials exist and key is valid
            load_dotenv(override=True)
            private_key = os.getenv("SOLANA_PRIVATE_KEY")
            if not private_key:
                if verbose:
                    logger.debug("Solana private key not found in environment")
                return False

            # Validate the key format
            Keypair.from_base58_string(private_key)

            # We successfully validated the private key exists and is in correct format
            if verbose:
                logger.debug("Solana configuration is valid")
            return True

        except Exception as e:
            if verbose:
                error_msg = str(e)
                if isinstance(e, SolanaConfigurationError):
                    error_msg = f"Configuration error: {error_msg}"
                elif isinstance(e, SolanaConnectionError):
                    error_msg = f"API validation error: {error_msg}"
                logger.debug(f"Solana Configuration validation failed: {error_msg}")
            return False

    def transfer(
        self, to_address: str, amount: float, token_mint: Optional[str] = None
    ) -> str:
        res = SolanaTransferHelper.transfer(
            self._get_connection_async(),
            self._get_wallet(),
            to_address,
            amount,
            token_mint,
        )
        res = asyncio.run(res)
        logger.debug(f"Transferred {amount} to {to_address}\nTransaction ID: {res}")
        return res

    # todo: test on mainnet
    def trade(
        self,
        output_mint: str,
        input_amount: float,
        input_mint: Optional[str] = SPL_TOKENS["USDC"],
        slippage_bps: int = 100,
    ) -> str:
        """Trade tokens using Jupiter"""
        logger.info(f"Swapping {input_amount} for {output_mint}")
        
        # Get cached instances with proper type hints
        wallet = self._get_wallet()
        async_client = self._get_connection_async()
        jupiter = self._get_jupiter(wallet, async_client)
        
        # Use config with proper type casting
        config = cast(SolanaConfig, self.config)
        
        res = TradeManager.trade(
            async_client,
            wallet,
            jupiter,
            output_mint,
            input_amount,
            input_mint,
            slippage_bps,
        )
        res = asyncio.run(res)
        return res

    def get_balance(self, token_address: str = None) -> float:
        if not token_address:
            logger.info("Getting SOL balance")
        else:
            logger.info(f"Getting balance for {token_address}")
        res = SolanaReadHelper.get_balance(
            self._get_connection_async(), self._get_wallet(), token_address
        )
        res = asyncio.run(res)
        return res

    def stake(self, amount: float) -> str:
        logger.info(f"Staking {amount} SOL")
        res = StakeManager.stake_with_jup(
            self._get_connection_async(), self._get_wallet(), amount
        )
        res = asyncio.run(res)
        logger.debug(f"Staked {amount} SOL\nTransaction ID: {res}")
        return res

    # todo: test on mainnet
    def lend_assets(self, amount: float) -> str:
        return "Not implemented"
        # logger.info(f"STUB: Lend {amount}")
        # res = AssetLender.lend_asset(
        #     self._get_connection_async(), self._get_wallet(), amount
        # )
        # res = asyncio.run(res)
        # logger.debug(f"Lent {amount} USDC\nTransaction ID: {res}")
        # return res

    def request_faucet(self) -> str:
        logger.info("Requesting faucet funds")
        res = FaucetManager.request_faucet_funds(self)
        res = asyncio.run(res)
        logger.debug(f"Requested faucet funds\nTransaction ID: {res}")
        return res

    def deploy_token(self, decimals: int = 9) -> str:
        return "Not implemented"
        # logger.info(f"STUB: Deploy token with {decimals} decimals")
        # res = TokenDeploymentManager.deploy_token(
        #     self._get_connection_async(), self._get_wallet(), decimals
        # )
        # res = asyncio.run(res)
        # logger.debug(
        #     f"Deployed token with {decimals} decimals\nToken Mint: {res['mint']}"
        # )
        # return res["mint"]

    def fetch_price(self, token_id: str) -> float:
        return SolanaReadHelper.fetch_price(token_id)

    # todo: test on mainnet
    def get_tps(self) -> int:
        res = SolanaPerformanceTracker.fetch_current_tps(self._get_connection_async())
        res = asyncio.run(res)
        return res

    def get_token_by_ticker(self, ticker: str) -> str:
        ticker = ticker.upper()
        if ticker in SPL_TOKENS:
            return SPL_TOKENS[ticker]
        return SolanaReadHelper.get_token_by_ticker(ticker)

    def get_token_by_address(self, mint: str) -> Dict[str, Any]:
        return SolanaReadHelper.get_token_by_address(mint)

    # todo: test on mainnet
    def launch_pump_token(
        self,
        token_name: str,
        token_ticker: str,
        description: str,
        image_url: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        return "Not implemented"
        # logger.info(f"STUB: Launch Pump & Fun token {token_ticker}")
        # res = PumpfunTokenManager.launch_pumpfun_token(
        #    self._get_connection_async(),
        #    self._get_wallet(),
        #    token_name,
        #    token_ticker,
        #    description,
        #    image_url,
        #    options,
        # )
        # res = asyncio.run(res)
        # logger.debug(
        #    f"Launched Pump & Fun token {token_ticker}\nToken Mint: {res['mint']}"
        # )
        # return res

    def perform_action(self, action_name: str, **kwargs: Any) -> Any:
        """Execute an action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        # Call the appropriate method based on action name
        method_name = action_name.replace("-", "_")
        method = getattr(self, method_name)
        return method(**kwargs)
