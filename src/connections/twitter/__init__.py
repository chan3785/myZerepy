from typing import Any, List
from nest.core import Module
from .controllers.cli_controller import TwitterCliController
from .service import TwitterService

from .service import TwitterService


# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [TwitterCliController]

# providers
PROVIDERS: List[Any] = [TwitterService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class TwitterModule:
    pass
