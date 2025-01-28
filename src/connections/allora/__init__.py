from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import AlloraCliController
from .service import AlloraService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [AlloraCliController]

# providers
PROVIDERS: List[Any] = [AlloraService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class AlloraModule:
    pass
