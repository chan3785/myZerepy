from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import GaladrielCliController
from .service import GaladrielService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [GaladrielCliController]

# providers
PROVIDERS: List[Any] = [GaladrielService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class GaladrielModule:
    pass
