from typing import Any, List
from nest.core import Module

from src.agent.agent_controller import AgentController
from src.agent.agent_service import AgentService
from ..connections.twitter.service import TwitterService

# imports
IMPORTS: List[Any] = []

# controllers
CONTROLLERS: List[Any] = [AgentController]

# providers
PROVIDERS: List[Any] = [AgentService, TwitterService]

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class AgentModule:
    pass
