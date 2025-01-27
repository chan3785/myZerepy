from typing import Any, List
from nest.core import Module
from .solana_service import SolanaService
from .controllers.cli_controller import SolanaCliController
import logging


logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [SolanaCliController]

# providers
PROVIDERS: List[Any] = [SolanaService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class SolanaModule:
    pass
