from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import GoatCliController
from .service import GoatService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [GoatCliController]

# providers
PROVIDERS: List[Any] = [GoatService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class GoatModule:
    pass
