import os
from typing import Any, List
from nest.core import Injectable
from dotenv import load_dotenv
from anthropic import Anthropic, NotFoundError
import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.anthropic import AnthropicConfig

logger = logging.getLogger(__name__)


@Injectable
class AnthropicService:
    def get_cfg(self, cfg: AnthropicConfig) -> dict[str, Any]:
        return cfg.model_dump()

    def generate_text(self, cfg: AnthropicConfig, prompt: str, system_prompt: str, model: str = None, **kwargs) -> str:
        """Generate text using Anthropic models"""
        try:
            client = self._get_client()
            
            # Use configured model if none provided 
            if not model:
                model = cfg.model

            message = client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }
                ],
            )
            return message.content[0].text
            
        except Exception as e:
            raise ValueError(f"Text generation failed: {str(e)}")

    def check_model(self, cfg: AnthropicConfig, model: str, **kwargs) -> bool:
        """Check if a specific model is available"""
        try:
            client = self._get_client()
            try:
                client.models.retrieve(model_id=model)
                return True
            except NotFoundError:
                logging.error("Model not found.")
                return False
            except Exception as e:
                raise ValueError(f"Model check failed: {e}")
                
        except Exception as e:
            raise ValueError(f"Model check failed: {e}")

    def list_models(self, cfg: AnthropicConfig, **kwargs) -> None:
        """List all available Anthropic models"""
        try:
            client = self._get_client()
            response = client.models.list().data
            model_ids = [model.id for model in response]

            logger.info("\nCLAUDE MODELS:")
            for i, model in enumerate(model_ids):
                logger.info(f"{i+1}. {model}")
                
        except Exception as e:
            raise ValueError(f"Listing models failed: {e}")