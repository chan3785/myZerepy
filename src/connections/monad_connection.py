import logging
import os
import time
import requests
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv, set_key
from web3 import Web3
from web3.middleware import geth_poa_middleware
from src.constants.networks import EVM_NETWORKS
from src.constants.abi import ERC20_ABI
from src.connections.base_connection import BaseConnection, Action, ActionParameter

logger = logging.getLogger("connections.monad_connection")

# Constants specific to Monad testnet
MONAD_BASE_GAS_PRICE = 50  # gwei - hardcoded for testnet

class MonadConnectionError(Exception):
    """Base exception for Monad connection errors"""
    pass

class MonadConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing Monad connection...")
        self._web3 = None
        self.NATIVE_TOKEN = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        
        # Get network configuration
        self.rpc_url = config.get("rpc")
        if not self.rpc_url:
            raise ValueError("RPC URL must be provided in config")
            
        self.scanner_url = "testnet.monadexplorer.com"
        self.chain_id = config.get("chain_id", 10143) 
        
        super().__init__(config)
        self._initialize_web3()

    def _get_explorer_link(self, tx_hash: str) -> str:
        """Generate block explorer link for transaction"""
        return f"https://{self.scanner_url}/tx/{tx_hash}"

    def _initialize_web3(self) -> None:
        """Initialize Web3 connection with retry logic"""
        if not self._web3:
            for attempt in range(3):
                try:
                    self._web3 = Web3(Web3.HTTPProvider(self.rpc_url))
                    self._web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                    if not self._web3.is_connected():
                        raise MonadConnectionError("Failed to connect to Monad network")
                    
                    chain_id = self._web3.eth.chain_id
                    if chain_id != self.chain_id:
                        raise MonadConnectionError(f"Connected to wrong chain. Expected {self.chain_id}, got {chain_id}")
                        
                    logger.info(f"Connected to Monad network with chain ID: {chain_id}")
                    break
                    
                except Exception as e:
                    if attempt == 2:
                        raise MonadConnectionError(f"Failed to initialize Web3 after 3 attempts: {str(e)}")
                    logger.warning(f"Web3 initialization attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(1)

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Monad configuration from JSON"""
        if "rpc" not in config:
            raise ValueError("RPC URL must be provided in config")
        return config

    def register_actions(self) -> None:
        """Register available Monad actions"""
        self.actions = {
            "get-balance": Action(
                name="get-balance",
                parameters=[
                    ActionParameter("address", False, str, "Address to check balance for (optional)"),
                    ActionParameter("token_address", False, str, "Token address (optional, native token if not provided)")
                ],
                description="Get native or token balance"
            ),
            "transfer": Action(
                name="transfer", 
                parameters=[
                    ActionParameter("to_address", True, str, "Recipient address"),
                    ActionParameter("amount", True, float, "Amount to transfer"),
                    ActionParameter("token_address", False, str, "Token address (optional, native token if not provided)")
                ],
                description="Send native token or tokens"
            ),
            "get-address": Action(
                name="get-address",
                parameters=[],
                description="Get your Monad wallet address"
            )
        }

    def configure(self) -> bool:
        """Sets up Monad wallet"""
        logger.info("\n⛓️ MONAD SETUP")
        
        if self.is_configured():
            logger.info("Monad connection is already configured")
            response = input("Do you want to reconfigure? (y/n): ")
            if response.lower() != 'y':
                return True

        try:
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write('')

            # Get wallet private key
            private_key = input("\nEnter your wallet private key: ")
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
                
            # Validate private key format
            if len(private_key) != 66 or not all(c in '0123456789abcdefABCDEF' for c in private_key[2:]):
                raise ValueError("Invalid private key format")
            
            # Test private key by deriving address
            account = self._web3.eth.account.from_key(private_key)
            logger.info(f"\nDerived address: {account.address}")
            
            # Save credentials
            set_key('.env', 'MONAD_PRIVATE_KEY', private_key)

            logger.info("\n✅ Monad configuration saved successfully!")
            return True

        except Exception as e:
            logger.error(f"Configuration failed: {str(e)}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        """Check if Monad connection is properly configured"""
        try:
            load_dotenv()
            private_key = os.getenv('MONAD_PRIVATE_KEY')
            if not private_key:
                if verbose:
                    logger.error("Missing MONAD_PRIVATE_KEY in .env")
                return False

            if not self._web3 or not self._web3.is_connected():
                if verbose:
                    logger.error("Not connected to Monad network")
                return False
                
            # Test account access
            account = self._web3.eth.account.from_key(private_key)
            balance = self._web3.eth.get_balance(account.address)
            return True

        except Exception as e:
            if verbose:
                logger.error(f"Configuration check failed: {str(e)}")
            return False

    def get_address(self) -> str:
        """Get the wallet address"""
        try:
            private_key = os.getenv('MONAD_PRIVATE_KEY')
            account = self._web3.eth.account.from_key(private_key)
            return f"Your Monad address: {account.address}"
        except Exception as e:
            return f"Failed to get address: {str(e)}"

    def get_balance(self, token_address: Optional[str] = None) -> float:
        """Get native or token balance for the configured wallet"""
        try:
            private_key = os.getenv('MONAD_PRIVATE_KEY')
            if not private_key:
                return "No wallet private key configured in .env"
            
            account = self._web3.eth.account.from_key(private_key)
            
            if token_address is None or token_address.lower() == self.NATIVE_TOKEN.lower():
                raw_balance = self._web3.eth.get_balance(account.address)
                return self._web3.from_wei(raw_balance, 'ether')
            
            contract = self._web3.eth.contract(
                address=Web3.to_checksum_address(token_address), 
                abi=ERC20_ABI 
            )
            decimals = contract.functions.decimals().call()
            raw_balance = contract.functions.balanceOf(account.address).call()
            return raw_balance / (10 ** decimals)
            
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return 0

    def _prepare_transfer_tx(
        self, 
        to_address: str,
        amount: float,
        token_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Prepare transfer transaction with Monad-specific gas handling"""
        try:
            private_key = os.getenv('MONAD_PRIVATE_KEY')
            account = self._web3.eth.account.from_key(private_key)
            
            # Get latest nonce
            nonce = self._web3.eth.get_transaction_count(account.address)
            
            # Use fixed gas price for testnet
            gas_price = Web3.to_wei(MONAD_BASE_GAS_PRICE, 'gwei')
            
            if token_address and token_address.lower() != self.NATIVE_TOKEN.lower():
                # Prepare ERC20 transfer
                contract = self._web3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=ERC20_ABI
                )
                decimals = contract.functions.decimals().call()
                amount_raw = int(amount * (10 ** decimals))
                
                # Monad charges based on gas limit, not usage
                tx = contract.functions.transfer(
                    Web3.to_checksum_address(to_address),
                    amount_raw
                ).build_transaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gasPrice': gas_price,
                    'chainId': self.chain_id
                })
            else:
                # Prepare native token transfer
                tx = {
                    'nonce': nonce,
                    'to': Web3.to_checksum_address(to_address),
                    'value': self._web3.to_wei(amount, 'ether'),
                    'gas': 21000,
                    'gasPrice': gas_price,
                    'chainId': self.chain_id
                }
            
            return tx

        except Exception as e:
            logger.error(f"Failed to prepare transaction: {str(e)}")
            raise

    def transfer(
        self,
        to_address: str,
        amount: float,
        token_address: Optional[str] = None
    ) -> str:
        """Transfer tokens with Monad-specific balance validation"""
        try:
            # Check balance including gas cost since Monad charges on gas limit
            gas_cost = Web3.to_wei(MONAD_BASE_GAS_PRICE * 21000, 'gwei')
            total_required = amount + self._web3.from_wei(gas_cost, 'ether')
            
            current_balance = self.get_balance(token_address=token_address)
            if current_balance < total_required:
                raise ValueError(
                    f"Insufficient balance. Required: {total_required}, Available: {current_balance}"
                )

            # Prepare and send transaction
            tx = self._prepare_transfer_tx(to_address, amount, token_address)
            private_key = os.getenv('MONAD_PRIVATE_KEY')
            account = self._web3.eth.account.from_key(private_key)
            
            signed = account.sign_transaction(tx)
            tx_hash = self._web3.eth.send_raw_transaction(signed.rawTransaction)
            
            tx_url = self._get_explorer_link(tx_hash.hex())
            return f"Transaction sent: {tx_url}"

        except Exception as e:
            logger.error(f"Transfer failed: {str(e)}")
            raise

    def perform_action(self, action_name: str, kwargs: Dict[str, Any]) -> Any:
        """Execute a Monad action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        load_dotenv()
        
        if not self.is_configured(verbose=True):
            raise MonadConnectionError("Monad connection is not properly configured")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs)