from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.connection_configs.goat import GoatConfig

logger = logging.getLogger(__name__)


@Injectable
class GoatService:
    def _get_all_goat_cfgs(self) -> dict[str, GoatConfig]:
        res: dict[str, GoatConfig] = ZEREPY_CONFIG.get_configs_by_connection("goat")
        return res

    def _get_goat_cfg(self, agent: str) -> GoatConfig:
        res: GoatConfig = ZEREPY_CONFIG.get_agent(agent).get_connection("goat")
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, GoatConfig] = self._get_all_goat_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_goat_cfg(agent).model_dump()
