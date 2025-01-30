from typing import Any, Dict, List
from nest.core import Injectable
import logging
from src.config.agent_config.connection_configs.allora import AlloraConfig

logger = logging.getLogger(__name__)


@Injectable
class AlloraService:
    def get_cfg(self, cfg: AlloraConfig) -> dict[str, Any]:
        return cfg.model_dump()

    async def get_inference(self, cfg: AlloraConfig, topic_id: int) -> Dict[str, Any]:
        """Get inference from Allora Network for a specific topic"""
        try:
            client = cfg._get_client()
            response = await client.get_inference_by_topic_id(topic_id)
            return {
                "topic_id": topic_id,
                **cfg.format_inference_data(response.inference_data),
            }
        except Exception as e:
            raise Exception(f"Failed to get inference: {str(e)}")

    async def list_topics(self, cfg: AlloraConfig) -> List[Dict[str, Any]]:
        """List all available Allora Network topics"""
        try:
            client = cfg._get_client()
            return await client.get_all_topics()
        except Exception as e:
            raise Exception(f"Failed to list topics: {str(e)}")
