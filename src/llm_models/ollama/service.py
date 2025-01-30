from typing import Any
import requests
import json
from nest.core import Injectable
import logging

from src.config.agent_config.model_configs.ollama import OllamaConfig
from src.config.zerepy_config import ZEREPY_CONFIG

logger = logging.getLogger(__name__)

@Injectable
class OllamaService:
    def get_cfg(self, cfg: OllamaConfig) -> dict[str, Any]:
        return cfg.model_dump()

    async def generate_text(
        self, 
        cfg: OllamaConfig,
        prompt: str, 
        system_prompt: str
    ) -> str:
        """Generate text using Ollama API with streaming support"""
        try:
            url = f"{cfg.base_url}/api/generate"
            payload = {
                "model": cfg.model,
                "prompt": prompt,
                "system": system_prompt,
            }
            response = requests.post(url, json=payload, stream=True)

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            # Initialize an empty string to store the complete response
            full_response = ""

            # Process each line of the response as a JSON object
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse the JSON object
                        data = json.loads(line.decode("utf-8"))
                        # Append the "response" field to the full response
                        full_response += data.get("response", "")
                    except json.JSONDecodeError as e:
                        raise Exception(f"Failed to parse JSON: {e}")

            return full_response

        except Exception as e:
            raise Exception(f"Text generation failed: {e}")

    async def test_connection(self, cfg: OllamaConfig) -> bool:
        """Test if Ollama is reachable"""
        try:
            url = f"{cfg.base_url}/api/models"
            response = requests.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False