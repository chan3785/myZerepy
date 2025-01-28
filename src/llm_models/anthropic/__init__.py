from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import AnthropicCliController
from .service import AnthropicService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [AnthropicCliController]

# providers
PROVIDERS: List[Any] = [AnthropicService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class AnthropicModule:
    pass
