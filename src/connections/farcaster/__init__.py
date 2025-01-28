from typing import Any, List
from nest.core import Module
import logging
from .controllers.cli_controller import FarcasterCliController
from .service import FarcasterService

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [FarcasterCliController]

# providers
PROVIDERS: List[Any] = [FarcasterService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class FarcasterModule:
    pass
