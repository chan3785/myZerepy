from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.openai import OpenAIConfig

logger = logging.getLogger(__name__)


@Injectable
class OpenAIService:
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
