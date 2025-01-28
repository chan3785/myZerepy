from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import HyperbolicCliController
from .service import HyperbolicService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [HyperbolicCliController]

# providers
PROVIDERS: List[Any] = [HyperbolicService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class HyperbolicModule:
    pass
