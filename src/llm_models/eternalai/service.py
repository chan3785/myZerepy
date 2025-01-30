from typing import Any, List
import os
from nest.core import Injectable
import logging
from openai import OpenAI
import requests
from web3 import Web3

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.eternalai import EternalAIConfig

logger = logging.getLogger(__name__)

AGENT_CONTRACT_ABI = [{"inputs": [{"internalType": "uint256","name": "_agentId","type": "uint256"}],"name": "getAgentSystemPrompt","outputs": [{"internalType": "bytes[]","name": "","type": "bytes[]"}],"stateMutability": "view","type": "function"}]
IPFS = "ipfs://"
LIGHTHOUSE_IPFS = "https://gateway.lighthouse.storage/ipfs/"
GCS_ETERNAL_AI_BASE_URL = "https://cdn.eternalai.org/upload/"

@Injectable
class EternalAIService:
    def _get_all_eternalai_cfgs(self) -> dict[str, EternalAIConfig]:
        res: dict[str, EternalAIConfig] = ZEREPY_CONFIG.get_configs_by_connection(
            "eternalai"
        )
        return res

    def _get_eternalai_cfg(self, agent: str) -> EternalAIConfig:
        res: EternalAIConfig = ZEREPY_CONFIG.get_agent(agent).get_connection(
            "eternalai"
        )
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, EternalAIConfig] = self._get_all_eternalai_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_eternalai_cfg(agent).model_dump()

    def _get_client(self, cfg: EternalAIConfig) -> OpenAI:
        """Get or create EternalAI client"""
        api_key = os.getenv("EternalAI_API_KEY")
        api_url = os.getenv("EternalAI_API_URL")
        if not api_key or not api_url:
            raise Exception("EternalAI credentials not found in environment")
        return OpenAI(api_key=api_key, base_url=api_url)

    def _get_on_chain_system_prompt_content(self, on_chain_data: str) -> str:
        if IPFS in on_chain_data:
            light_house = on_chain_data.replace(IPFS, LIGHTHOUSE_IPFS)
            response = requests.get(light_house)
            if response.status_code == 200:
                return response.text
            else:
                gcs = on_chain_data.replace(IPFS, GCS_ETERNAL_AI_BASE_URL)
                response = requests.get(gcs)
                if response.status_code == 200:
                    return response.text
                else:
                    raise Exception(f"invalid on-chain system prompt response status{response.status_code}")
        else:
            if len(on_chain_data) > 0:
                return on_chain_data
            else:
                raise Exception(f"invalid on-chain system prompt")

    async def generate_text(
        self, 
        cfg: EternalAIConfig,
        prompt: str,
        system_prompt: str,
        model: str = None,
        chain_id: str = None,
    ) -> str:
        """Generate text using EternalAI models"""
        try:
            client = self._get_client(cfg)
            model = model or cfg.model
            logger.info(f"Using model {model}")

            chain_id = chain_id or cfg.chain_id
            if not chain_id:
                chain_id = "45762"
            logger.info(f"Using chain_id {chain_id}")

            # Handle on-chain system prompt if configured
            if cfg.agent_id and cfg.contract_address and cfg.rpc_url:
                logger.info(f"agent_id: {cfg.agent_id}, contract_address: {cfg.contract_address}")
                web3 = Web3(Web3.HTTPProvider(cfg.rpc_url))
                logger.info(f"web3 connected to {cfg.rpc_url} {web3.is_connected()}")
                contract = web3.eth.contract(address=cfg.contract_address, abi=AGENT_CONTRACT_ABI)
                result = contract.functions.getAgentSystemPrompt(cfg.agent_id).call()
                logger.info(f"on-chain system_prompt: {result}")
                if len(result) > 0:
                    try:
                        system_prompt = self._get_on_chain_system_prompt_content(result[0].decode("utf-8"))
                        logging.info(f"new system_prompt: {system_prompt}")
                    except Exception as e:
                        logger.error(f"get on-chain system_prompt fail {e}")

            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                extra_body={"chain_id": chain_id}
            )

            if completion.choices is None:
                raise Exception("Text generation failed: completion.choices is None")

            try:
                if completion.onchain_data is not None:
                    logger.info(f"response onchain data: {json.dumps(completion.onchain_data, indent=4)}")
            except:
                logger.info(f"response onchain data object: {completion.onchain_data}")
            
            return completion.choices[0].message.content

        except Exception as e:
            raise Exception(f"Text generation failed: {e}")

    async def check_model(self, cfg: EternalAIConfig, model: str) -> bool:
        """Check if a specific model is available"""
        try:
            client = self._get_client(cfg)
            try:
                client.models.retrieve(model=model)
                return True
            except Exception:
                return False
        except Exception as e:
            raise Exception(f"Model check failed: {e}")

    async def list_models(self, cfg: EternalAIConfig) -> List[str]:
        """List all available EternalAI models"""
        try:
            client = self._get_client(cfg)
            response = client.models.list().data

            # Filter for fine-tuned models
            fine_tuned_models = [
                model.id for model in response
                if model.owned_by in ["organization", "user", "organization-owner"]
            ]

            return fine_tuned_models

        except Exception as e:
            raise Exception(f"Listing models failed: {e}")