import logging
import os
from typing import Dict, Any,Optional
from dotenv import load_dotenv
import asyncio

from agentipy import SolanaAgentKit

# solana
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed

# solders
from solders.keypair import Keypair  # type: ignore

# src
from src.connections.base_connection import BaseConnection, Action, ActionParameter


logger = logging.getLogger("connections.solana_connection")

class SolanaConnectionError(Exception):
    """Base exception for Solana connection errors"""
    pass
class SolanaConfigurationError(SolanaConnectionError):
    """Raised when there are configuration/credential issues"""
    pass

class SolanaConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing Solana connection...")
        super().__init__(config)

    @property
    def is_llm_provider(self) -> bool:
        return False
    def _get_agent(self) -> SolanaAgentKit:
        credentials = self._get_credentials()
        agent = SolanaAgentKit(
            credentials["SOLANA_PRIVATE_KEY"],
            self.config['rpc'],
            ""
        )
        return agent
    def _get_connection(self) -> Client:
        conn = Client(self.config['rpc'])
        if not conn.is_connected():
            raise SolanaConnectionError("rpc invalid connection")
        return conn
    def _get_wallet(self):
        creds = self._get_credentials()
        return Keypair.from_base58_string(creds['SOLANA_PRIVATE_KEY'])
    def _get_credentials(self) -> Dict[str, str]:
        """Get Solana credentials from environment with validation"""
        logger.debug("Retrieving Solana Credentials")
        load_dotenv()
        required_vars = {
            "SOLANA_PRIVATE_KEY": "solana wallet private key"
        }
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
        

        
        
        Keypair.from_base58_string(credentials['SOLANA_PRIVATE_KEY'])
        logger.debug("All required credentials found")
        return credentials

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Solana configuration from JSON"""
        required_fields = ["rpc"]
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
            
        if not isinstance(config["rpc"], str):
            raise ValueError("rpc must be a positive integer")
            
        return config  # For stub, accept any config

    def register_actions(self) -> None:
        """Register available Solana actions"""
        self.actions = {
            "transfer": Action(
                name="transfer",
                parameters=[
                    ActionParameter("to_address", True, str, "Destination address"),
                    ActionParameter("amount", True, float, "Amount to transfer"),
                    ActionParameter("token_mint", False, str, "Token mint address (optional for SOL)")
                ],
                description="Transfer SOL or SPL tokens"
            ),
            "trade": Action(
                name="trade",
                parameters=[
                    ActionParameter("output_mint", True, str, "Output token mint address"),
                    ActionParameter("input_amount", True, float, "Input amount"),
                    ActionParameter("input_mint", False, str, "Input token mint (optional for SOL)"),
                    ActionParameter("slippage_bps", False, int, "Slippage in basis points")
                ],
                description="Swap tokens using Jupiter"
            ),
            "get-balance": Action(
                name="get-balance",
                parameters=[
                    ActionParameter("token_address", False, str, "Token mint address (optional for SOL)")
                ],
                description="Check SOL or token balance"
            ),
            "stake": Action(
                name="stake",
                parameters=[
                    ActionParameter("amount", True, float, "Amount of SOL to stake")
                ],
                description="Stake SOL"
            ),
            "lend-assets": Action(
                name="lend-assets",
                parameters=[
                    ActionParameter("amount", True, float, "Amount to lend")
                ],
                description="Lend assets"
            ),
            "request-faucet": Action(
                name="request-faucet",
                parameters=[],
                description="Request funds from faucet for testing"
            ),
            "deploy-token": Action(
                name="deploy-token",
                parameters=[
                    ActionParameter("decimals", False, int, "Token decimals (default 9)")
                ],
                description="Deploy a new token"
            ),
            "fetch-price": Action(
                name="fetch-price",
                parameters=[
                    ActionParameter("token_id", True, str, "Token ID to fetch price for")
                ],
                description="Get token price"
            ),
            "get-tps": Action(
                name="get-tps",
                parameters=[],
                description="Get current Solana TPS"
            ),
            "get-token-by-ticker": Action(
                name="get-token-by-ticker",
                parameters=[
                    ActionParameter("ticker", True, str, "Token ticker symbol")
                ],
                description="Get token data by ticker symbol"
            ),
            "get-token-by-address": Action(
                name="get-token-by-address",
                parameters=[
                    ActionParameter("mint", True, str, "Token mint address")
                ],
                description="Get token data by mint address"
            ),
            "launch-pump-token": Action(
                name="launch-pump-token",
                parameters=[
                    ActionParameter("token_name", True, str, "Name of the token"),
                    ActionParameter("token_ticker", True, str, "Token ticker symbol"),
                    ActionParameter("description", True, str, "Token description"),
                    ActionParameter("image_url", True, str, "Token image URL"),
                    ActionParameter("options", False, dict, "Additional token options")
                ],
                description="Launch a Pump & Fun token"
            )
        }
    def configure(self) -> bool:
        """Stub configuration"""
        return True

    def is_configured(self, verbose: bool = True) -> bool:
        """Stub configuration check"""
        try:

            credentials = self._get_credentials()
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
        return True

    def transfer(self, to_address: str, amount: float, token_mint: Optional[str] = None) -> bool:
        logger.info(f"STUB: Transfer {amount} to {to_address}")

        agent = self._get_agent()

        res=asyncio.run(agent.transfer(to_address,amount,token_mint))

        logger.info(res)

        return True
            
    def trade(self, output_mint: str, input_amount: float, 
             input_mint: Optional[str], slippage_bps: int = 100) -> bool:
        logger.info(f"STUB: Swap {input_amount} for {output_mint}")
        agent = self._get_agent()
        res=asyncio.run(agent.trade(output_mint,input_amount,input_mint,slippage_bps))
        return True
#works
    def get_balance(self, token_address: Optional[str] = None) -> float:
        agent = self._get_agent()
        return asyncio.run(agent.get_balance(token_address))

    def stake(self, amount: float) -> bool:
        logger.info(f"STUB: Stake {amount} SOL")
        agent = self._get_agent()
        asyncio.run(agent.stake(amount))
        return True

    def lend_assets(self, amount: float) -> bool:
        logger.info(f"STUB: Lend {amount}")
        agent = self._get_agent()
        asyncio.run(agent.lend_assets(amount))
        return True

    def request_faucet(self) -> bool:
        logger.info("STUB: Requesting faucet funds")
        agent = self._get_agent()
        asyncio.run(agent.request_faucet_funds())
        return True
    def deploy_token(self, decimals: int = 9) -> str:
        agent = self._get_agent()
        res=asyncio.run(agent.deploy_token(decimals))
        return res
    def fetch_price(self, token_id: str) -> float:
        agent = self._get_agent()
        res=asyncio.run(agent.fetch_price(token_id))
        return float(res)
#works
    def get_tps(self) -> int:
        agent = self._get_agent()
        res=asyncio.run(agent.get_tps())
        return res
#works
    def get_token_by_ticker(self, ticker: str) -> Dict[str, Any]:
        agent = self._get_agent()
        res=asyncio.run(agent.get_token_data_by_ticker(ticker))
        return res
#works
    def get_token_by_address(self, mint: str) -> Dict[str, Any]:
        agent = self._get_agent()
        res=asyncio.run(agent.get_token_data_by_address(mint))
        return res

    def launch_pump_token(self, token_name: str, token_ticker: str, 
                         description: str, image_url: str, 
                         options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        agent = self._get_agent()
        res=asyncio.run(agent.launch_pump_fun_token(token_name,token_ticker,description,image_url,options))
        return res
    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a Solana action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs)
    