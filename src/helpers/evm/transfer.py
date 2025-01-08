from web3 import Web3

from src.constants import GAS, GAS_PRICE, GAS_PRICE_UNIT
from src.helpers.evm import get_public_key_from_private_key


class EvmTransferHelper:
    @staticmethod
    def transfer_evm(
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

    # @staticmethod
    # def transfer_token(connection: EvmConnection, to_address: str, amount_in_tokens: float) -> str:
