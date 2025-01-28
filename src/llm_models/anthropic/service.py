from typing import Any, List
from nest.core import Injectable

import logging

from ...config.zerepy_config import ZEREPY_CONFIG
from ...config.agent_config.model_configs.anthropic import AnthropicConfig

logger = logging.getLogger(__name__)


@Injectable
class AnthropicService:
    def _get_all_anthropic_cfgs(self) -> dict[str, AnthropicConfig]:
        res: dict[str, AnthropicConfig] = ZEREPY_CONFIG.get_configs_by_connection(
            "anthropic"
        )
        return res

    def _get_anthropic_cfg(self, agent: str) -> AnthropicConfig:
        res: AnthropicConfig = ZEREPY_CONFIG.get_agent(agent).get_connection(
            "anthropic"
        )
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, AnthropicConfig] = self._get_all_anthropic_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_anthropic_cfg(agent).model_dump()
