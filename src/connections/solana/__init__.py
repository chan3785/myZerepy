from typing import Any, List
from nest.core import Module

import logging

from src.solana.controllers.cli_controller import SolanaCliController
from src.solana.solana_service import SolanaService


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
