import os
from typing import Any
import logging
from dotenv import load_dotenv
from openai import OpenAI
from nest.core import Injectable

from src.config.agent_config.connection_configs.openai import OpenAIConfig

logger = logging.getLogger(__name__)

@Injectable
class OpenAIService:
    def get_cfg(self, cfg: OpenAIConfig) -> dict[str, Any]:
        return cfg.model_dump()

    def _get_client(self) -> OpenAI:
        """Get or create OpenAI client"""
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment")
        return OpenAI(api_key=api_key)

    async def generate_text(
        self,
        cfg: OpenAIConfig,
        prompt: str,
        system_prompt: str,
        model: str = None,
    ) -> str:
        """Generate text using OpenAI models"""
        try:
            client = self._get_client()
            
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
            raise ValueError(f"Text generation failed: {str(e)}")

    async def check_model(self, cfg: OpenAIConfig, model: str) -> bool:
        """Check if a specific model is available"""
        try:
            client = self._get_client()
            try:
                client.models.retrieve(model=model)
                return True
            except Exception:
                return False
        except Exception as e:
            raise ValueError(f"Model check failed: {str(e)}")

    async def list_models(self, cfg: OpenAIConfig) -> None:
        """List all available OpenAI models"""
        try:
            client = self._get_client()
            response = client.models.list().data
            
            # Filter for fine-tuned models
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
            raise ValueError(f"Listing models failed: {str(e)}")