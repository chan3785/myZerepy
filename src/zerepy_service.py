from nest.core import Injectable

import logging

from src.config.base_config import BASE_CONFIG


logger = logging.getLogger(__name__)


@Injectable
class ZerePyService:
    cfg = BASE_CONFIG

    def version(self) -> str:
        return f"ZerePy version: {self.cfg.version}"
