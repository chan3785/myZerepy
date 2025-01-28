from typing import Any, List
from nest.core import Module
import logging
from .eternalai import EternalAIModule
from .anthropic import AnthropicModule
from .galadriel import GaladrielModule
from .hyperbolic import HyperbolicModule
from .ollama import OllamaModule
from .openai import OpenAIModule

logger = logging.getLogger(__name__)


# imports
IMPORTS: List[Any] = [
    EternalAIModule,
    AnthropicModule,
    GaladrielModule,
    HyperbolicModule,
    OllamaModule,
    OpenAIModule,
]

# controllers
CONTROLLERS: List[Any] = []

# providers
PROVIDERS: List[Any] = []

# exports
EXPORTS: List[Any] = []


@Module(
    imports=IMPORTS,
    controllers=CONTROLLERS,
    providers=PROVIDERS,
    exports=EXPORTS,
)
class LlmModelsModule:
    pass
