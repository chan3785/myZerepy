import os
import logging
from typing import Any
from nest.core import Injectable
from openai import OpenAI
from dotenv import load_dotenv

from src.config.agent_config.model_configs.galadriel import GaladrielConfig

logger = logging.getLogger(__name__)

@Injectable
class GaladrielService:
    def get_cfg(self, cfg: GaladrielConfig) -> dict[str, Any]:
        return cfg.model_dump()

    def _get_client(self, cfg: GaladrielConfig) -> OpenAI:
        """Get or create Galadriel client"""
        api_key = os.getenv("GALADRIEL_API_KEY")
        if not api_key:
            raise Exception("Galadriel API key not found in environment")

        headers = {}
        if fine_tune_api_key := os.getenv("GALADRIEL_FINE_TUNE_API_KEY"):
            headers["Fine-Tune-Authorization"] = f"Bearer {fine_tune_api_key}"
            
        return OpenAI(
            api_key=api_key, 
            base_url="https://api.galadriel.com/v1/verified", 
            default_headers=headers
        )

    def generate_text(
        self, 
        cfg: GaladrielConfig,
        prompt: str, 
        system_prompt: str, 
        model: str = None
    ) -> str:
        """Generate text using Galadriel models"""
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

    def check_model(self, cfg: GaladrielConfig, model: str) -> bool:
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

    def list_models(self, cfg: GaladrielConfig) -> None:
        """List all available models"""
        try:
            client = self._get_client(cfg)
            response = client.models.list().data

            # Filter for fine-tuned models
            fine_tuned_models = [
                model for model in response
                if model.owned_by in ["organization", "user", "organization-owner"]
            ]

            return fine_tuned_models

        except Exception as e:
            raise Exception(f"Listing models failed: {e}")