from web3 import Web3
from src.helpers.evm import get_public_key_from_private_key
from src.helpers.evm.contract import EvmContractHelper


class EvmReadHelper:
    @staticmethod
    async def get_balance(
        web3: Web3, private_key: str, token_address: str = None
    ) -> float:
        pub_key = get_public_key_from_private_key(private_key)
        if token_address:
            return await EvmReadHelper._get_balance_tokens(web3, pub_key, token_address)
        return await EvmReadHelper._get_balance(web3, pub_key)

    @staticmethod
    async def _get_balance(web3: Web3, pub_key: str) -> float:
        balance = web3.eth.get_balance(pub_key)
        return balance / 10**18

    @staticmethod
    async def _get_balance_tokens(
        web3: Web3, pub_key: str, token_address: str
    ) -> float:
        balance = EvmContractHelper.read_contract(
            web3, token_address, "balanceOf", pub_key
        )
        decimals = EvmContractHelper.read_contract(web3, token_address, "decimals")
        return balance / 10**decimals
