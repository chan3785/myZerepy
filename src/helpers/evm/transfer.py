from web3 import Web3

from src.constants import GAS, GAS_PRICE, GAS_PRICE_UNIT
from src.helpers.evm import get_public_key_from_private_key
from src.helpers.evm.contract import EvmContractHelper
from src.helpers.evm.etherscan import EtherscanHelper


class EvmTransferHelper:
    @staticmethod
    async def transfer(
        web3: Web3,
        priv_key: str,
        to_address: str,
        amount_in_ether: float,
        token_address: str = None,
    ) -> str:
        if token_address:
            return await EvmTransferHelper._transfer_tokens(
                web3, priv_key, to_address, amount_in_ether, token_address
            )
        return EvmTransferHelper._transfer(web3, priv_key, to_address, amount_in_ether)

    @staticmethod
    def _transfer(
        web3: Web3, priv_key: str, to_address: str, amount_in_ether: float
    ) -> str:

        pub_key = get_public_key_from_private_key(priv_key)
        nonce = web3.eth.get_transaction_count(pub_key)
        amount_in_wei = web3.to_wei(amount_in_ether, "ether")
        transaction = {
            "to": to_address,
            "value": amount_in_wei,
            "nonce": nonce,
            "gas": GAS,
            "gasPrice": web3.to_wei(GAS_PRICE, GAS_PRICE_UNIT),
        }
        signed_transaction = web3.eth.account.sign_transaction(transaction, priv_key)
        tx_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        return tx_hash.hex()

    @staticmethod
    async def _transfer_tokens(
        web3: Web3,
        priv_key: str,
        to_address: str,
        amount_in_tokens: float,
        token_address: str,
    ) -> str:
        pub_key = get_public_key_from_private_key(priv_key)
        nonce = web3.eth.get_transaction_count(pub_key)
        decimals = EvmContractHelper.read_contract(web3, token_address, "decimals")
        amount_in_wei = int(amount_in_tokens * 10**decimals)
        abi = EtherscanHelper.get_contract_abi(token_address)
        contract = web3.eth.contract(address=token_address, abi=abi)
        transaction = {
            "to": token_address,
            "data": contract.functions.transfer(
                to_address, amount_in_wei
            ).buildTransaction(
                {
                    "nonce": nonce,
                    "gas": GAS,
                    "gasPrice": web3.toWei(GAS_PRICE, GAS_PRICE_UNIT),
                }
            ),
        }
        signed_transaction = web3.eth.account.sign_transaction(transaction, priv_key)
        tx_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        return tx_hash.hex()
