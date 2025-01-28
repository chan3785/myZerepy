from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import OpenAICliController
from .service import OpenAIService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [OpenAICliController]

# providers
PROVIDERS: List[Any] = [OpenAIService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class OpenAIModule:
    pass
