from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import EternalAICliController
from .service import EternalAIService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [EternalAICliController]

# providers
PROVIDERS: List[Any] = [EternalAIService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class EternalAIModule:
    pass
