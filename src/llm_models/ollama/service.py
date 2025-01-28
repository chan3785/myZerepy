from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.ollama import OllamaConfig

logger = logging.getLogger(__name__)


@Injectable
class OllamaService:
    def _get_all_ollama_cfgs(self) -> dict[str, OllamaConfig]:
        res: dict[str, OllamaConfig] = ZEREPY_CONFIG.get_configs_by_connection("ollama")
        return res

    def _get_ollama_cfg(self, agent: str) -> OllamaConfig:
        res: OllamaConfig = ZEREPY_CONFIG.get_agent(agent).get_connection("ollama")
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, OllamaConfig] = self._get_all_ollama_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_ollama_cfg(agent).model_dump()
