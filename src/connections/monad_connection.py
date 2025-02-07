import logging
import os
import requests
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key
from web3 import Web3
from web3.middleware import geth_poa_middleware
from src.constants.abi import ERC20_ABI
from src.connections.base_connection import BaseConnection, Action, ActionParameter

logger = logging.getLogger("connections.monad_connection")

class MonadConnectionError(Exception):
    """Base exception for Monad connection errors"""
    pass

class MonadConnection(BaseConnection):
    
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing Monad connection...")
        self._web3 = None
        
        # Get RPC configuration directly from config
        self.rpc_url = config.get("rpc")
        if not self.rpc_url:
            raise ValueError("RPC URL must be provided in config")
            
        # Set explorer URL - update this when Monad explorer is available
        self.explorer = "https://explorer.monad.xyz"  # Placeholder - update when available
        
        super().__init__(config)
        self._initialize_web3()
        self.ERC20_ABI = ERC20_ABI
        self.NATIVE_TOKEN = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"  # Standard native token address

    def _get_explorer_link(self, tx_hash: str) -> str:
        """Generate block explorer link for transaction"""
        return f"{self.explorer}/tx/{tx_hash}"

    def _initialize_web3(self):
        """Initialize Web3 connection"""
        if not self._web3:
            self._web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            self._web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            if not self._web3.is_connected():
                raise MonadConnectionError("Failed to connect to Monad network")
            
            try:
                chain_id = self._web3.eth.chain_id
                logger.info(f"Connected to Monad network with chain ID: {chain_id}")
            except Exception as e:
                logger.warning(f"Could not get chain ID: {e}")

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Monad configuration from JSON"""
        required = ["rpc"]
        missing = [field for field in required if field not in config]
        if missing:
            raise ValueError(f"Missing config fields: {', '.join(missing)}")
            
        if not isinstance(config["rpc"], str):
            raise ValueError("RPC URL must be a string")
            
        return config

    def get_token_by_ticker(self, ticker: str) -> Optional[str]:
        """Get token address by ticker symbol"""
        try:
            # This would need to be updated with actual Monad token lookup logic
            # For now, returning None as placeholder
            return None

        except Exception as error:
            logger.error(f"Error fetching token address: {str(error)}")
            return None

    def register_actions(self) -> None:
        self.actions = {
            "get-token-by-ticker": Action(
                name="get-token-by-ticker",
                parameters=[
                    ActionParameter("ticker", True, str, "Token ticker symbol to look up")
                ],
                description="Get token address by ticker symbol"
            ),
            "get-balance": Action(
                name="get-balance",
                parameters=[
                    ActionParameter("address", False, str, "Address to check balance for"),
                    ActionParameter("token_address", False, str, "Optional token address")
                ],
                description="Get native token or ERC20 token balance"
            ),
            "transfer": Action(
                name="transfer",
                parameters=[
                    ActionParameter("to_address", True, str, "Recipient address"),
                    ActionParameter("amount", True, float, "Amount to transfer"),
                    ActionParameter("token_address", False, str, "Optional token address")
                ],
                description="Send native token or ERC20 tokens"
            )
        }

    def configure(self) -> bool:
        logger.info("\n🔷 MONAD CHAIN SETUP")
        if self.is_configured():
            logger.info("Monad connection is already configured")
            response = input("Do you want to reconfigure? (y/n): ")
            if response.lower() != 'y':
                return True

        try:
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write('')

            private_key = input("\nEnter your wallet private key: ")
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            set_key('.env', 'MONAD_PRIVATE_KEY', private_key)

            if not self._web3.is_connected():
                raise MonadConnectionError("Failed to connect to Monad network")

            account = self._web3.eth.account.from_key(private_key)
            logger.info(f"\n✅ Successfully connected with address: {account.address}")
            return True

        except Exception as e:
            logger.error(f"Configuration failed: {e}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        try:
            load_dotenv()
            if not os.getenv('MONAD_PRIVATE_KEY'):
                if verbose:
                    logger.error("Missing MONAD_PRIVATE_KEY in .env")
                return False

            if not self._web3.is_connected():
                if verbose:
                    logger.error("Not connected to Monad network")
                return False
            return True

        except Exception as e:
            if verbose:
                logger.error(f"Configuration check failed: {e}")
            return False

    def get_balance(self, address: Optional[str] = None, token_address: Optional[str] = None) -> float:
        """Get balance for an address or the configured wallet"""
        try:
            if not address:
                private_key = os.getenv('MONAD_PRIVATE_KEY')
                if not private_key:
                    raise MonadConnectionError("No wallet configured")
                account = self._web3.eth.account.from_key(private_key)
                address = account.address

            if token_address:
                contract = self._web3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=self.ERC20_ABI
                )
                balance = contract.functions.balanceOf(address).call()
                decimals = contract.functions.decimals().call()
                return balance / (10 ** decimals)
            else:
                balance = self._web3.eth.get_balance(address)
                return self._web3.from_wei(balance, 'ether')

        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            raise

    def transfer(self, to_address: str, amount: float, token_address: Optional[str] = None) -> str:
        """Transfer native token or ERC20 tokens to an address"""
        try:
            private_key = os.getenv('MONAD_PRIVATE_KEY')
            account = self._web3.eth.account.from_key(private_key)
            chain_id = self._web3.eth.chain_id
            
            if token_address:
                contract = self._web3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=self.ERC20_ABI
                )
                decimals = contract.functions.decimals().call()
                amount_raw = int(amount * (10 ** decimals))
                
                tx = contract.functions.transfer(
                    Web3.to_checksum_address(to_address),
                    amount_raw
                ).build_transaction({
                    'from': account.address,
                    'nonce': self._web3.eth.get_transaction_count(account.address),
                    'gasPrice': self._web3.eth.gas_price,
                    'chainId': chain_id
                })
            else:
                tx = {
                    'nonce': self._web3.eth.get_transaction_count(account.address),
                    'to': Web3.to_checksum_address(to_address),
                    'value': self._web3.to_wei(amount, 'ether'),
                    'gas': 21000,
                    'gasPrice': self._web3.eth.gas_price,
                    'chainId': chain_id
                }

            signed = account.sign_transaction(tx)
            tx_hash = self._web3.eth.send_raw_transaction(signed.rawTransaction)

            # Log and return explorer link immediately
            tx_link = self._get_explorer_link(tx_hash.hex())
            return f"⛓️ Transfer transaction sent: {tx_link}"

        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            raise

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a Monad action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        load_dotenv()
        
        if not self.is_configured(verbose=True):
            raise MonadConnectionError("Monad is not properly configured")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs)