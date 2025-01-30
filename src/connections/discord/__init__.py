from typing import Any, List
from nest.core import Module
from .service import DiscordService
from .controllers.cli_controller import DiscordCliController
import logging

logger = logging.getLogger(__name__)

# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [DiscordCliController]

# providers
PROVIDERS: List[Any] = [DiscordService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class DiscordModule:
    pass
