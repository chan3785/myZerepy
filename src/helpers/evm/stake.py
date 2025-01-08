from venv import logger

from web3 import Web3

from src.helpers.evm.contract import EvmContractHelper
from src.constants import ROCKET_POOL_STAKING_CONTRACT_ADDRESS


class EvmStakeHelper:
    @staticmethod
    async def stake(
        web3: Web3,
        private_key: str,
        amount_in_ether: float,
    ) -> str:
        logger.info("Staking with Rocket Pool")
        res = await EvmContractHelper._call(
            web3,
            private_key,
            ROCKET_POOL_STAKING_CONTRACT_ADDRESS,
            "deposit",
            amount_in_ether,
        )
        return res
