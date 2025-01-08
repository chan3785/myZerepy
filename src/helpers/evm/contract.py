from venv import logger
from typing import Any
from src.helpers.evm import get_public_key_from_private_key
from src.helpers.evm.etherscan import EtherscanHelper
from web3 import Web3
from src.constants import GAS, GAS_PRICE, GAS_PRICE_UNIT


class EvmContractHelper:
    @staticmethod
    async def read_contract(
        web3: Web3, contract_address: str, method: str, *args
    ) -> Any:
        logger.info(
            f"STUB: Call contract {contract_address} method {method} with {args}"
        )
        abi = await EtherscanHelper.get_contract_abi(contract_address)
        contract = web3.eth.contract(address=contract_address, abi=abi)
        return contract.functions[method](*args).call()

    @staticmethod
    async def _call(
        web3: Web3,
        private_key: str,
        contract_address: str,
        method: str,
        value: int = 0,
        *args,
    ) -> Any:
        logger.info(
            f"STUB: Call contract {contract_address} method {method} with {args}"
        )
        abi = await EtherscanHelper.get_contract_abi(contract_address)
        contract = web3.eth.contract(address=contract_address, abi=abi)
        pub_key = get_public_key_from_private_key(private_key)
        nonce = web3.eth.get_transaction_count(pub_key)
        tx = contract.functions[method](*args).build_transaction(
            {
                "value": value,
                "gas": GAS,
                "gasPrice": web3.to_wei(GAS_PRICE, GAS_PRICE_UNIT),
                "nonce": nonce,
            }
        )
        # sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        # send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()
