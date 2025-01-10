from venv import logger
from web3 import Web3
from src.helpers.evm import get_public_key_from_private_key
from src.helpers.evm.contract import EvmContractHelper
import requests
from pycoingecko import CoinGeckoAPI


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

    @staticmethod
    def get_coin_by_address(cg: CoinGeckoAPI, address: str) -> str:
        coin = cg.get_coin_info_from_contract_address_by_id("ethereum", address)
        return coin["name"]

    """ 
    @staticmethod
    async def fetch_price(web3: Web3, contract_address: str) -> float:
        logger.info(f"{EvmReadHelper.get_coin_by_ticker()}") """

    @staticmethod
    def get_coin_by_ticker(cg: CoinGeckoAPI, ticker: str) -> str:
        ticker = ticker.lower()
        coins = cg.get_coins_list()
        # logger.debug(f"Coins: {coins}")
        for coin in coins:
            if coin["symbol"] == ticker:
                data = cg.get_coin_by_id(coin["id"])
                # logger.debug(f"\n\nData: {data}\n\n")
                res = []
                res.append(data["name"])
                res.append(data["symbol"])
                res.append(str(data["market_data"]["current_price"]["usd"]))
                for platform in data["platforms"]:
                    res.append(f"{platform}: {data['platforms'][platform]}")
                return "\n".join(res)
