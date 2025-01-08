import json
from typing import List, Dict, Any
from aioetherscan import Client as EtherscanClient
from asyncio_throttle import Throttler
from aiohttp_retry import ExponentialRetry
from venv import logger
from dotenv import load_dotenv
import os
from src.helpers.evm import parse_abi_string


class EtherscanHelper:
    @staticmethod
    def _client() -> EtherscanClient:
        # load .env file
        load_dotenv()

        # get api key from environment
        api_key = os.getenv("ETHERSCAN_KEY")

        # if api key is not found, raise an error
        if not api_key:
            logger.error("ETHERSCAN_KEY not found in environment")
            raise ValueError("ETHERSCAN_KEY not found in environment")
        logger.debug(f'Found Etherscan API Key: {api_key}')

        # create a client
        throttler = Throttler(rate_limit=5, period=1)
        retry_options = ExponentialRetry(attempts=3)
        c = EtherscanClient(api_key=api_key, throttler=throttler, retry_options=retry_options)

        return c

    # static method "get_contract_abi" to get the ABI of a contract. returns a list of dictionaries with strings as keys and values as Any
    @staticmethod
    async def get_contract_abi(contract_address: str) -> List[Dict[str, Any]]:
        # create a client
        client = EtherscanHelper._client()

        # get the contract ABI
        abi = await client.contract.contract_abi(contract_address)
        parsed_abi = parse_abi_string(abi)
        await client.close()
        return parsed_abi

