from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.galadriel import GaladrielConfig

logger = logging.getLogger(__name__)


@Injectable
class GaladrielService:
    def _get_all_galadriel_cfgs(self) -> dict[str, GaladrielConfig]:
        res: dict[str, GaladrielConfig] = ZEREPY_CONFIG.get_configs_by_connection(
            "galadriel"
        )
        return res

    def _get_galadriel_cfg(self, agent: str) -> GaladrielConfig:
        res: GaladrielConfig = ZEREPY_CONFIG.get_agent(agent).get_connection(
            "galadriel"
        )
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, GaladrielConfig] = self._get_all_galadriel_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_galadriel_cfg(agent).model_dump()
