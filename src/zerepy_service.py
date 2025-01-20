from nest.core import Injectable

import os
import logging

logger = logging.getLogger(__name__)


@Injectable
class ZerePyService:
    def version(self) -> str:
        return "zerepy v0.2.0"

    def is_configured(self) -> bool:
        return True
