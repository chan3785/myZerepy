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
    def __init__(self):
        self._client = None

    def _get_all_anthropic_cfgs(self) -> dict[str, AnthropicConfig]:
        res: dict[str, AnthropicConfig] = ZEREPY_CONFIG.get_configs_by_connection("anthropic")
        return res

    def _get_anthropic_cfg(self, agent: str) -> AnthropicConfig:
        res: AnthropicConfig = ZEREPY_CONFIG.get_agent(agent).get_connection("anthropic")
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, AnthropicConfig] = self._get_all_anthropic_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_anthropic_cfg(agent).model_dump()

    def _get_client(self) -> Anthropic:
        """Get or create Anthropic client"""
        if not self._client:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found in environment")
            self._client = Anthropic(api_key=api_key)
        return self._client

    def generate_text(self, prompt: str, system_prompt: str, model: str = None, **kwargs) -> str:
        """Generate text using Anthropic models"""
        try:
            client = self._get_client()
            
            # Use configured model if none provided
            if not model:
                model = self._get_anthropic_cfg("default").model

            message = client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            return message.content[0].text
            
        except Exception as e:
            raise ValueError(f"Text generation failed: {e}")

    def check_model(self, model: str, **kwargs) -> bool:
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

    def list_models(self, **kwargs) -> None:
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