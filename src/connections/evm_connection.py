# std
import asyncio
import os
import logging
from typing import Any, Dict, List, Optional

# dotenv
from dotenv import load_dotenv

# web3
from web3 import Web3

# src
from src.connections.base_connection import Action, ActionParameter, BaseConnection
from src.helpers.evm.transfer import EvmTransferHelper
from src.helpers.evm.contract import EvmContractHelper
from src.helpers.evm.etherscan import EtherscanHelper
from src.constants import EVM_TOKENS
from src.helpers.evm import get_public_key_from_private_key


logger = logging.getLogger("connections.evm_connection")


class EvmConnectionError(Exception):
    """Base exception for Evm connection errors"""

    pass


class EvmConfigurationError(EvmConnectionError):
    """Raised when there are configuration/credential issues"""

    pass


class EvmConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing Evm connection...")
        super().__init__(config)

    @property
    def is_llm_provider(self) -> bool:
        return False

    def _get_connection(self) -> Web3:
        w3 = Web3(Web3.HTTPProvider(self.config["rpc"]))
        if not w3.is_connected():
            raise EvmConnectionError("Evm connection failed")
        w3.middleware_onion.clear()
        # w3.eth.set_gas_price_strategy(node_default_gas_price_strategy)
        return w3

    def _get_private_key(self):
        creds = self._get_credentials()
        private_key = creds["EVM_PRIVATE_KEY"]
        return private_key

    def _get_etherscan_url(self) -> str:
        creds = self._get_credentials()
        api_key = creds["ETHERSCAN_KEY"]
        return f"https://api.etherscan.io/api?apikey={api_key}"

    def _get_credentials(self) -> Dict[str, str]:
        """Get Evm credentials from environment with validation"""
        logger.debug("Retrieving Evm Credentials")
        load_dotenv()
        required_vars = {
            "EVM_PRIVATE_KEY": "evm wallet private key",
            "ETHERSCAN_KEY": "etherscan API key",
        }
        credentials = {}
        missing = []

        for env_var, description in required_vars.items():
            value = os.getenv(env_var)
            if not value:
                missing.append(description)
            credentials[env_var] = value

        if missing:
            error_msg = f"Missing Evm credentials: {', '.join(missing)}"
            raise EvmConfigurationError(error_msg)

        logger.debug("All required credentials found")
        return credentials

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Evm configuration from JSON"""
        required_fields = ["rpc"]
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValueError(
                f"Missing required configuration fields: {', '.join(missing_fields)}"
            )

        if not isinstance(config["rpc"], str):
            raise ValueError("rpc must be a positive integer")

        return config  # For stub, accept any config

    def register_actions(self) -> None:
        """Register available Evm actions"""
        self.actions = {
            "transfer": Action(
                name="transfer",
                parameters=[
                    ActionParameter("to_address", True, str, "Destination address"),
                    ActionParameter(
                        "amount_in_ether", True, float, "Amount to transfer"
                    ),
                    ActionParameter(
                        "token_address",
                        False,
                        str,
                        "Token contract address (optional for ETH)",
                    ),
                ],
                description="Transfer EVM or ERC20 tokens",
            ),
            "trade": Action(
                name="trade",
                parameters=[
                    ActionParameter(
                        "output_mint", True, str, "Output token mint address"
                    ),
                    ActionParameter("input_amount", True, float, "Input amount"),
                    ActionParameter(
                        "input_mint", False, str, "Input token mint (optional for EVM)"
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
                        True,
                        str,
                        "Token mint address (optional for EVM)",
                    )
                ],
                description="Check EVM or token balance",
            ),
            "stake": Action(
                name="stake",
                parameters=[
                    ActionParameter("amount", True, float, "Amount of EVM to stake")
                ],
                description="Stake EVM",
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
                name="get-tps", parameters=[], description="Get current Evm TPS"
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
            "list-contract-functions": Action(
                name="list-contract-functions",
                parameters=[
                    ActionParameter("contract_address", True, str, "Contract address")
                ],
                description="List functions of a contract",
            ),
            "call-contract": Action(
                name="call-contract",
                parameters=[
                    ActionParameter("contract_address", True, str, "Contract address"),
                    ActionParameter("method", True, str, "Method name"),
                    ActionParameter("args", False, list, "Method arguments"),
                ],
                description="Call a contract method",
            ),
            "wrap-eth": Action(
                name="wrap-eth",
                parameters=[
                    ActionParameter(
                        "amount_in_ether", True, float, "Amount of ETH to wrap"
                    )
                ],
                description="Wrap ETH to WETH",
            ),
        }

    def configure(self) -> bool:
        """Stub configuration"""
        return True

    def is_configured(self, verbose: bool = True) -> bool:
        """Stub configuration check"""
        try:

            credentials = self._get_credentials()
            logger.debug("Evm configuration is valid")
            return True

        except Exception as e:
            if verbose:
                error_msg = str(e)
                if isinstance(e, EvmConfigurationError):
                    error_msg = f"Configuration error: {error_msg}"
                elif isinstance(e, EvmConnectionError):
                    error_msg = f"API validation error: {error_msg}"
                logger.debug(f"Evm Configuration validation failed: {error_msg}")
            return False
        return True

    def transfer(
        self, to_address: str, amount_in_ether: int, token_address: str = None
    ) -> str:
        logger.info(f"STUB: Transfer {amount_in_ether} to {to_address}")
        res = EvmTransferHelper.transfer(
            self._get_connection(),
            self._get_private_key(),
            to_address,
            amount_in_ether,
            token_address,
        )
        res = asyncio.run(res)
        logger.debug(
            f"Transferred {amount_in_ether} to {to_address}\nTransaction ID: {res}"
        )
        return res

    def trade(
        self,
        output_mint: str,
        input_amount: float,
        input_mint: Optional[str] = EVM_TOKENS["WETH"],
        slippage_bps: int = 100,
    ) -> str:
        logger.info(f"STUB: Swap {input_amount} for {output_mint}")
        # res=EvmTradeHelper.trade(self, output_mint, input_amount, input_mint, slippage_bps)
        # logger.info(f"Swapped {input_amount} for {output_mint}\nTransaction ID: {res}")

        return "Not implemented"

    def get_balance(self, token_address: str) -> float:
        logger.info(f"STUB: Get balance")
        web3 = self._get_connection()
        priv_key = self._get_private_key()
        pub_key = get_public_key_from_private_key(priv_key)
        balance = asyncio.run(
            EvmContractHelper.read_contract(web3, token_address, "balanceOf", pub_key)
        )
        decimals = asyncio.run(
            EvmContractHelper.read_contract(web3, token_address, "decimals")
        )
        balance = balance / 10**decimals

        return balance

    def stake(self, amount: float) -> str:
        logger.info(f"STUB: Stake {amount}")

        return "Not implemented"

    def lend_assets(self, amount: float) -> str:
        logger.info(f"STUB: Lend {amount}")
        return "Not implemented"

    def request_faucet(self) -> str:
        logger.info(f"STUB: Request faucet")
        return "Not implemented"

    def deploy_token(self, decimals: int = 9) -> str:
        logger.info(f"STUB: Deploy token with {decimals} decimals")
        return "Not implemented"

    def fetch_price(self, token_id: str) -> str:
        logger.info(f"STUB: Fetch price for {token_id}")
        return "Not implemented"

    def get_tps(self) -> int:
        logger.info(f"STUB: Get TPS")
        raise NotImplementedError("Not implemented")
        # return 100

    def get_token_by_ticker(self, ticker: str) -> Dict[str, Any]:
        logger.info(f"STUB: Get token by ticker {ticker}")
        raise NotImplementedError("Not implemented")

        # return {}

    def get_token_by_address(self, mint: str) -> Dict[str, Any]:
        logger.info(f"STUB: Get token by mint {mint}")
        raise NotImplementedError("Not implemented")
        # return {}

    def wrap_eth(self, amount_in_ether: float) -> str:
        logger.info(f"STUB: Wrap {amount_in_ether}")
        web3 = self._get_connection()
        amount_in_wei = web3.to_wei(amount_in_ether, "ether")
        res = asyncio.run(
            EvmContractHelper._call(
                self._get_connection(),
                self._get_private_key(),
                EVM_TOKENS["WETH"],
                "deposit",
                amount_in_wei,
            )
        )
        return res

    def list_contract_functions(self, contract_address: str) -> List:
        logger.info(f"STUB: List contract functions for {contract_address}")
        abi = asyncio.run(EtherscanHelper.get_contract_abi(contract_address))
        res_str = ""
        """
        example output:
        1. function_name1
            arg1:
                name: arg1_name
                type: arg1_type
            arg2:
                name: arg2_name
                type: arg2_type
        2. function_name2
            arg1:
                name: arg1_name
                type: arg1_type
            arg2:
                name: arg2_name
                type: arg2_type 

        """
        for x, func in enumerate(abi, 1):
            if func["type"] == "function":
                res_str += f"\n{x}. {func['name']}\n"
                for input in func["inputs"]:
                    res_str += f"\t{input['name']}:\n"
                    res_str += f"\t\tname: {input['name']}\n"
                    res_str += f"\t\ttype: {input['type']}\n"

        return res_str

    def call_contract(self, contract_address: str, method: str, args=[]) -> Any:
        logger.info(
            f"STUB: Call contract {contract_address} method {method} with {args}"
        )
        res = asyncio.run(
            EvmContractHelper.read_contract(
                self._get_connection(), contract_address, method, *args
            )
        )
        return res

    # todo: test on mainnet
    def launch_pump_token(
        self,
        token_name: str,
        token_ticker: str,
        description: str,
        image_url: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        logger.info(f"STUB: Launch Pump & Fun token")
        raise NotImplementedError("Not implemented")
        # return {}

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a Evm action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace("-", "_")
        method = getattr(self, method_name)
        return method(**kwargs)
