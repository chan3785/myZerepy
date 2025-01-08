import datetime
import decimal
import os
import sys
import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_keys import keys
from eth_utils import decode_hex

from eth_defi.provider.multi_provider import create_multi_provider_web3
from eth_defi.revert_reason import fetch_transaction_revert_reason
from eth_defi.token import fetch_erc20_details
from eth_defi.confirmation import wait_transactions_to_complete
from eth_defi.uniswap_v3.constants import UNISWAP_V3_DEPLOYMENTS
from eth_defi.uniswap_v3.deployment import fetch_deployment
from eth_defi.uniswap_v3.swap import swap_with_slippage_protection

from src.connections.base_connection import Action, ActionParameter, BaseConnection
from src.constants import GAS, GAS_PRICE, GAS_PRICE_UNIT

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
        w3 = Web3(Web3.HTTPProvider(self.config['rpc']))
        if not w3.is_connected():
            raise EvmConnectionError("Evm connection failed")
        w3.middleware_onion.clear()
        #w3.eth.set_gas_price_strategy(node_default_gas_price_strategy)
        return w3

    def _get_pubkey(self):
        private_key = self._get_private_key()
        private_key_bytes = decode_hex(private_key)
        key = keys.PrivateKey(private_key_bytes)
        pub_key = key.public_key
        p=pub_key.to_checksum_address()
        logger.debug(f"Public key: {p}")
        return p
    
    def _get_private_key(self):
        creds = self._get_credentials()
        private_key = creds['EVM_PRIVATE_KEY']
        return private_key

    def _get_credentials(self) -> Dict[str, str]:
        """Get Evm credentials from environment with validation"""
        logger.debug("Retrieving Evm Credentials")
        load_dotenv()
        required_vars = {
            "EVM_PRIVATE_KEY": "evm wallet private key"
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
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
            
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
                    ActionParameter("amount_in_ether", True, float, "Amount to transfer"),
                    ActionParameter("token_address", False, str, "Token contract address (optional for ETH)")
                ],
                description="Transfer EVM or ERC20 tokens"
            ),
            "trade": Action(
                name="trade",
                parameters=[
                    ActionParameter("output_mint", True, str, "Output token mint address"),
                    ActionParameter("input_amount", True, float, "Input amount"),
                    ActionParameter("input_mint", False, str, "Input token mint (optional for EVM)"),
                    ActionParameter("slippage_bps", False, int, "Slippage in basis points")
                ],
                description="Swap tokens using Jupiter"
            ),
            "get-balance": Action(
                name="get-balance",
                parameters=[
                    ActionParameter("token_address", False, str, "Token mint address (optional for EVM)")
                ],
                description="Check EVM or token balance"
            ),
            "stake": Action(
                name="stake",
                parameters=[
                    ActionParameter("amount", True, float, "Amount of EVM to stake")
                ],
                description="Stake EVM"
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
                description="Get current Evm TPS"
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
#todo w
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

    def transfer(self, to_address: str, amount_in_ether: int, token_address: Optional[str] = None) -> bool:
        logger.info(f"STUB: Transfer {amount_in_ether} to {to_address}")
        if token_address:
            res = EvmTransferHelper.transfer_token(self, to_address, amount_in_ether)
            return True
        else:
            res = EvmTransferHelper.transfer_evm(self, to_address, amount_in_ether)
        logger.info(f"Transferred {amount_in_ether} to {to_address}\nTransaction ID: {res}")
        return True
       
# todo: test on mainnet
    def trade(self, output_mint: str, input_amount: float, 
             input_mint: Optional[str] = "0xdac17f958d2ee523a2206206994597c13d831ec7", slippage_bps: int = 100) -> bool:
        logger.info(f"STUB: Swap {input_amount} for {output_mint}")
        res=EvmTradeHelper.trade(self, output_mint, input_amount, input_mint, slippage_bps)
        logger.info(f"Swapped {input_amount} for {output_mint}\nTransaction ID: {res}")

        return True

    def get_balance(self, token_address: Optional[str] = None) -> float:
        logger.info(f"STUB: Get balance")
        
        return 1000.0

# todo: test on mainnet
    def stake(self, amount: float) -> bool:
        logger.info(f"STUB: Stake {amount}")

        return True

#todo: test on mainnet
    def lend_assets(self, amount: float) -> bool:
        logger.info(f"STUB: Lend {amount}")
        return True

    def request_faucet(self) -> bool:
        logger.info(f"STUB: Request faucet")
        return True

    def deploy_token(self, decimals: int = 9) -> str:
        logger.info(f"STUB: Deploy token with {decimals} decimals")
        return "0x1234567890123456789012345678901234567890"

    def fetch_price(self, token_id: str) -> float:
        logger.info(f"STUB: Fetch price for {token_id}")
        return 1.23
#todo: test on mainnet
    def get_tps(self) -> int:
        logger.info(f"STUB: Get TPS")
        return 100

    def get_token_by_ticker(self, ticker: str) -> Dict[str, Any]:
        logger.info(f"STUB: Get token by ticker {ticker}")
        return {}

    def get_token_by_address(self, mint: str) -> Dict[str, Any]:
        logger.info(f"STUB: Get token by mint {mint}")
        return {}

#todo: test on mainnet
    def launch_pump_token(self, token_name: str, token_ticker: str, 
                         description: str, image_url: str, 
                         options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"STUB: Launch Pump & Fun token")
        return {}


    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a Evm action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs)
    
class EvmTransferHelper:
    @staticmethod
    def transfer_evm(connection: EvmConnection, to_address: str, amount_in_ether: float) -> str:
        pub_key = connection._get_pubkey()
        priv_key = connection._get_private_key()
        w3 = connection._get_connection()
        nonce = w3.eth.get_transaction_count(pub_key)
        amount_in_wei = w3.to_wei(amount_in_ether, "ether")
        transaction = {
            "to": to_address,
            "value": amount_in_wei,
            "nonce": nonce,
            "gas": GAS,
            "gasPrice": w3.to_wei(GAS_PRICE, GAS_PRICE_UNIT),
        }
        signed_transaction = w3.eth.account.sign_transaction(transaction, priv_key)
        tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        return tx_hash.hex()

        

    #@staticmethod
    #def transfer_token(connection: EvmConnection, to_address: str, amount_in_tokens: float) -> str:

class EvmTradeHelper:
    @staticmethod
    def trade(connection: EvmConnection, output_token: str, input_amount: float, 
             input_token: Optional[str], slippage_bps: int = 100) -> str:
        QUOTE_TOKEN_ADDRESS=input_token
        BASE_TOKEN_ADDRESS=output_token
        private_key = connection._get_private_key()
        account: LocalAccount = Account.from_key(private_key)
        my_address = account.address
        web3=connection._get_connection()
        logger.debug(f"Connected to blockchain, chain id is {web3.eth.chain_id}. the latest block is {web3.eth.block_number:,}")

        # Grab Uniswap v3 smart contract addreses for Polygon.
        #
        deployment_data = UNISWAP_V3_DEPLOYMENTS["polygon"]
        uniswap_v3 = fetch_deployment(
            web3,
            factory_address=deployment_data["factory"],
            router_address=deployment_data["router"],
            position_manager_address=deployment_data["position_manager"],
            quoter_address=deployment_data["quoter"],
        )

        logger.debug(f"Using Uniwap v3 compatible router at {uniswap_v3.swap_router.address}")
        # Enable eth_sendTransaction using this private key
        web3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        # Read on-chain ERC-20 token data (name, symbol, etc.)
        base = fetch_erc20_details(web3, BASE_TOKEN_ADDRESS)
        quote = fetch_erc20_details(web3, QUOTE_TOKEN_ADDRESS)

        # Native token balance
        # See https://tradingstrategy.ai/glossary/native-token
        gas_balance = web3.eth.get_balance(account.address)

        print(f"Your address is {my_address}")
        print(f"Your have {base.fetch_balance_of(my_address)} {base.symbol}")
        print(f"Your have {quote.fetch_balance_of(my_address)} {quote.symbol}")
        print(f"Your have {gas_balance / (10 ** 18)} for gas fees")

        assert quote.fetch_balance_of(my_address) > 0, f"Cannot perform swap, as you have zero {quote.symbol} needed to swap"

        # Ask for transfer details
        decimal_amount = input(f"How many {quote.symbol} tokens you wish to swap to {base.symbol}? ")

        # Some input validation
        try:
            decimal_amount = Decimal(decimal_amount)
        except (ValueError, decimal.InvalidOperation) as e:
            raise AssertionError(f"Not a good decimal amount: {decimal_amount}") from e

        # Fat-fingering check
        print(f"Confirm swap amount {decimal_amount} {quote.symbol} to {base.symbol}")
        confirm = input("Ok [y/n]?")
        if not confirm.lower().startswith("y"):
            print("Aborted")
            sys.exit(1)

        # Convert a human-readable number to fixed decimal with 18 decimal places
        raw_amount = quote.convert_to_raw(decimal_amount)

        # Each DEX trade is two transactions
        # - ERC-20.approve()
        # - swap (various functions)
        # This is due to bad design of ERC-20 tokens,
        # more here https://twitter.com/moo9000/status/1619319039230197760

        # Uniswap router must be allowed to spent our quote token
        # and we do this by calling ERC20.approve() from our account
        # to the token contract.
        approve = quote.contract.functions.approve(uniswap_v3.swap_router.address, raw_amount)
        tx_1 = approve.build_transaction(
            {
                # approve() may take more than 500,000 gas on Arbitrum One
                "gas": 850_000,
                "from": my_address,
            }
        )

        #
        # Uniswap v3 may have multiple pools per
        # trading pair differetiated by the fee tier. For example
        # WETH-USDC has pools of 0.05%, 0.30% and 1%
        # fees. Check for different options
        # in https://tradingstrategy.ai/search
        #
        # Here we use 5 BPS fee pool (5/10,000).
        #
        #
        # Build a swap transaction with slippage protection
        #
        # Slippage protection is very important, or you
        # get instantly overrun by MEV bots with
        # sandwitch attacks
        #
        # https://tradingstrategy.ai/glossary/mev
        #
        #
        bound_solidity_func = swap_with_slippage_protection(
            uniswap_v3,
            base_token=base,
            quote_token=quote,
            max_slippage=20,  # Allow 20 BPS slippage before tx reverts
            amount_in=raw_amount,
            recipient_address=my_address,
            pool_fees=[500],   # 5 BPS pool WETH-USDC
        )

        tx_2 = bound_solidity_func.build_transaction(
            {
                # Uniswap swap should not take more than 1M gas units.
                # We do not use automatic gas estimation, as it is unreliable
                # and the number here is the maximum value only.
                # Only way to know this number is by trial and error
                # and experience.
                "gas": 1_000_000,
                "from": my_address,
            }
        )

        # Sign and broadcast the transaction using our private key
        tx_hash_1 = web3.eth.send_transaction(tx_1)
        tx_hash_2 = web3.eth.send_transaction(tx_2)

        # This will raise an exception if we do not confirm within the timeout.
        # If the timeout occurs the script abort and you need to
        # manually check the transaction hash in a blockchain explorer
        # whether the transaction completed or not.
        tx_wait_minutes = 2.5
        print(f"Broadcasted transactions {tx_hash_1.hex()}, {tx_hash_2.hex()}, now waiting {tx_wait_minutes} minutes for it to be included in a new block")
        print(f"View your transactions confirming at https://polygonscan/address/{my_address}")
        receipts = wait_transactions_to_complete(
            web3,
            [tx_hash_1, tx_hash_2],
            max_timeout=datetime.timedelta(minutes=tx_wait_minutes),
            confirmation_block_count=1,
        )

        # Check if any our transactions failed
        # and display the reason
        for completed_tx_hash, receipt in receipts.items():
            if receipt["status"] == 0:
                revert_reason = fetch_transaction_revert_reason(web3, completed_tx_hash)
                raise AssertionError(f"Our transaction {completed_tx_hash.hex()} failed because of: {revert_reason}")

        print("All ok!")
        print(f"After swap, you have {base.fetch_balance_of(my_address)} {base.symbol}")
        print(f"After swap, you have {quote.fetch_balance_of(my_address)} {quote.symbol}")
        print(f"After swap, you have {gas_balance / (10 ** 18)} native token left")


