from nest.core import Injectable

import logging

logger = logging.getLogger(__name__)


@Injectable
class OpenAiService:
    def hello(self) -> str:
        return "Hello, OpenAI!"
