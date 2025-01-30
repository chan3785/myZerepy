from typing import Any, List
from nest.core import Injectable
import os
from openai import OpenAI
import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.hyperbolic import HyperbolicConfig

logger = logging.getLogger(__name__)

@Injectable
class HyperbolicService:
    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs = ZEREPY_CONFIG.get_configs_by_connection("hyperbolic")
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return ZEREPY_CONFIG.get_agent(agent).get_connection("hyperbolic").model_dump()

    def _get_client(self, cfg: HyperbolicConfig) -> OpenAI:
        """Get or create Hyperbolic client"""
        api_key = os.getenv("HYPERBOLIC_API_KEY")
        if not api_key:
            raise Exception("Hyperbolic API key not found in environment")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.hyperbolic.xyz/v1"
        )

    async def generate_text(self, cfg: HyperbolicConfig, prompt: str, system_prompt: str, model: str | None = None) -> str:
        """Generate text using Hyperbolic models"""
        try:
            client = self._get_client(cfg)
            
            # Use configured model if none provided
            if not model:
                model = cfg.model

            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            return completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Text generation failed: {e}")

    async def check_model(self, cfg: HyperbolicConfig, model: str) -> bool:
        """Check if a specific model is available"""
        try:
            client = self._get_client(cfg)
            try:
                models = client.models.list()
                for hyperbolic_model in models.data:
                    if hyperbolic_model.id == model:
                        return True
                return False
            except Exception as e:
                raise Exception(f"Model check failed: {e}")
                
        except Exception as e:
            raise Exception(f"Model check failed: {e}")

    async def list_models(self, cfg: HyperbolicConfig) -> List[str]:
        """List all available Hyperbolic models"""
        try:
            client = self._get_client(cfg)
            response = client.models.list().data
            return [model.id for model in response]
                    
        except Exception as e:
            raise Exception(f"Listing models failed: {e}")