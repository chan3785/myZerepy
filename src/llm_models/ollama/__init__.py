from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import OllamaCliController
from .service import OllamaService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [OllamaCliController]

# providers
PROVIDERS: List[Any] = [OllamaService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class OllamaModule:
    pass
