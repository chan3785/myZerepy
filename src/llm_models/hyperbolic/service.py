from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.hyperbolic import HyperbolicConfig

logger = logging.getLogger(__name__)


@Injectable
class HyperbolicService:
    def _get_all_hyperbolic_cfgs(self) -> dict[str, HyperbolicConfig]:
        res: dict[str, HyperbolicConfig] = ZEREPY_CONFIG.get_configs_by_connection(
            "hyperbolic"
        )
        return res

    def _get_hyperbolic_cfg(self, agent: str) -> HyperbolicConfig:
        res: HyperbolicConfig = ZEREPY_CONFIG.get_agent(agent).get_connection(
            "hyperbolic"
        )
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, HyperbolicConfig] = self._get_all_hyperbolic_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_hyperbolic_cfg(agent).model_dump()
