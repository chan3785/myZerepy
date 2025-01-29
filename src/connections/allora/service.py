from typing import Any, Dict, List
from nest.core import Injectable
import logging
from allora_sdk.v2.api_client import AlloraAPIClient, ChainSlug
import asyncio
import os

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.connection_configs.allora import AlloraConfig

logger = logging.getLogger(__name__)

@Injectable
class AlloraService:
    def _get_all_allora_cfgs(self) -> dict[str, AlloraConfig]:
        res: dict[str, AlloraConfig] = ZEREPY_CONFIG.get_configs_by_connection("allora")
        return res

    def _get_allora_cfg(self, agent: str) -> AlloraConfig:
        res: AlloraConfig = ZEREPY_CONFIG.get_agent(agent).get_connection("allora")
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, AlloraConfig] = self._get_all_allora_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_allora_cfg(agent).model_dump()

    def get_inference(self, cfg: AlloraConfig, topic_id: int) -> Dict[str, Any]:
        """Get inference from Allora Network for a specific topic"""
        try:
            api_key = os.getenv("ALLORA_API_KEY")
            if not api_key:
                raise ValueError("Allora API key not found in environment")
            
            client = AlloraAPIClient(
                chain_slug=cfg.chain_slug,
                api_key=api_key
            )

            # Create event loop for async calls
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(client.get_inference_by_topic_id(topic_id))
                return {
                    "topic_id": topic_id,
                    "inference": response.inference_data.network_inference_normalized
                }
            finally:
                loop.close()
                
        except Exception as e:
            raise Exception(f"Failed to get inference: {str(e)}")

    def list_topics(self, cfg: AlloraConfig) -> List[Dict[str, Any]]:
        """List all available Allora Network topics"""
        try:
            api_key = os.getenv("ALLORA_API_KEY")
            if not api_key:
                raise ValueError("Allora API key not found in environment")
            
            client = AlloraAPIClient(
                chain_slug=cfg.chain_slug,
                api_key=api_key
            )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(client.get_all_topics())
            finally:
                loop.close()
                
        except Exception as e:
            raise Exception(f"Failed to list topics: {str(e)}")