from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.connection_configs.farcaster import FarcasterConfig

logger = logging.getLogger(__name__)


@Injectable
class FarcasterService:
    def _get_all_farcaster_cfgs(self) -> dict[str, FarcasterConfig]:
        res: dict[str, FarcasterConfig] = ZEREPY_CONFIG.get_configs_by_connection(
            "farcaster"
        )
        return res

    def _get_farcaster_cfg(self, agent: str) -> FarcasterConfig:
        res: FarcasterConfig = ZEREPY_CONFIG.get_agent(agent).get_connection(
            "farcaster"
        )
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, FarcasterConfig] = self._get_all_farcaster_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_farcaster_cfg(agent).model_dump()
