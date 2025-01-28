from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.connection_configs.allora import AlloraConfig

logger = logging.getLogger(__name__)


@Injectable
class AlloraService:
    def _get_all_allora_cfgs(self) -> dict[str, AlloraConfig]:
        res: dict[str, AlloraConfig] = ZEREPY_CONFIG.get_configs_by_connection("allora")
        return res

    def _get_allora_cfg(self, agent: str) -> AlloraConfig:
        res: AlloraConfig = ZEREPY_CONFIG.get_agent(agent).get_connection("allora")
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, AlloraConfig] = self._get_all_allora_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_allora_cfg(agent).model_dump()
