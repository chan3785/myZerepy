from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.eternalai import EternalAIConfig

logger = logging.getLogger(__name__)


@Injectable
class EternalAIService:
    def _get_all_eternalai_cfgs(self) -> dict[str, EternalAIConfig]:
        res: dict[str, EternalAIConfig] = ZEREPY_CONFIG.get_configs_by_connection(
            "eternalai"
        )
        return res

    def _get_eternalai_cfg(self, agent: str) -> EternalAIConfig:
        res: EternalAIConfig = ZEREPY_CONFIG.get_agent(agent).get_connection(
            "eternalai"
        )
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, EternalAIConfig] = self._get_all_eternalai_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_eternalai_cfg(agent).model_dump()
