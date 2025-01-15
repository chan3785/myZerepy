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

    # static method "get_contract_abi" to get the ABI of a contract. returns a list of dictionaries with strings as keys and values as Any
    @staticmethod
    async def get_contract_abi(
        client: EtherscanClient, contract_address: str
    ) -> List[Dict[str, Any]]:
        # create a client

        # get the contract ABI
        abi = await client.contract.contract_abi(contract_address)
        parsed_abi = parse_abi_string(abi)
        await client.close()
        return parsed_abi
