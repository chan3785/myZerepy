from typing import Any
from nest.core import Injectable

import logging

from src.config.zerepy_config import ZEREPY_CONFIG


logger = logging.getLogger(__name__)


@Injectable
class ZerePyService:
    cfg = ZEREPY_CONFIG

    def version(self) -> str:
        return f"ZerePy version: {self.cfg.version}"
