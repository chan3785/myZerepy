import os
from typing import Any, List
from nest.core import Injectable
from dotenv import load_dotenv
from openai import OpenAI
import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.openai import OpenAIConfig

logger = logging.getLogger(__name__)


@Injectable
class OpenAIService:
    def __init__(self):
        self._client = None

    def _get_all_openai_cfgs(self) -> dict[str, OpenAIConfig]:
        res: dict[str, OpenAIConfig] = ZEREPY_CONFIG.get_configs_by_connection("openai")
        return res

    def _get_openai_cfg(self, agent: str) -> OpenAIConfig:
        res: OpenAIConfig = ZEREPY_CONFIG.get_agent(agent).get_connection("openai")
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, OpenAIConfig] = self._get_all_openai_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_openai_cfg(agent).model_dump()

    def _get_client(self) -> OpenAI:
        """Get or create OpenAI client"""
        if not self._client:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found in environment")
            self._client = OpenAI(api_key=api_key)
        return self._client

    def generate_text(self, prompt: str, system_prompt: str, model: str = None, **kwargs) -> str:
        """Generate text using OpenAI models"""
        try:
            client = self._get_client()
            
            # Use configured model if none provided
            if not model:
                model = self._get_openai_cfg("default").model

            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )

            return completion.choices[0].message.content
            
        except Exception as e:
            raise ValueError(f"Text generation failed: {e}")

    def check_model(self, model, **kwargs):
        """Check if a specific model is available"""
        try:
            client = self._get_client()
            try:
                client.models.retrieve(model=model)
                # If we get here, the model exists
                return True
            except Exception:
                return False
        except Exception as e:
            raise ValueError(e)

    def list_models(self, **kwargs) -> None:
        """List all available OpenAI models"""
        try:
            client = self._get_client()
            response = client.models.list().data
            
            fine_tuned_models = [
                model for model in response 
                if model.owned_by in ["organization", "user", "organization-owner"]
            ]

            logger.info("\nGPT MODELS:")
            logger.info("1. gpt-3.5-turbo")
            logger.info("2. gpt-4")
            logger.info("3. gpt-4-turbo")
            logger.info("4. gpt-4o")
            logger.info("5. gpt-4o-mini")
            
            if fine_tuned_models:
                logger.info("\nFINE-TUNED MODELS:")
                for i, model in enumerate(fine_tuned_models):
                    logger.info(f"{i+1}. {model.id}")
                    
        except Exception as e:
            raise ValueError(f"Listing models failed: {e}")