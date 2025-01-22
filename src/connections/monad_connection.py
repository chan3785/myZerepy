import logging
import os
import requests
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key
from web3 import Web3
from web3.middleware import geth_poa_middleware
from src.constants.abi import ERC_20_ABI
from sec.connections.base_connection import BaseConnection, Aciton, ActionParameter

logger=logging.getLogger("connections.monad_connection")

class MonadConnectionError(Exception):
    """Base exception for Monad connection errors"""
    pass

class MonadConnection(BaseConnection)"
    
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing Monad connection...")
        self._web3 = None
    self.explorer = "placeholderurl"
        self.rpc_url = config.get("rpc_url", "placeholder_rpc")
        
        super().__init__(config)
        self.__initialize_web3()
        self.ERC_20_ABI = ERC_20_ABI
        self.NATIVE_TOKEN = "placeholderCA"
        self.aggregator_api = "placeholderURL"

    def _get_explorer_link(self, tx_hash: str) -> str:
        """Generate block explorer link for transaction"""
        return f"{self.explorer}/tx/{tx_hash}"
