from src.agent.agent_module import AgentModule
from src.solana.solana_module import SolanaModule


if __name__ == "__main__":
    # from nest.core.pynest_factory import PyNestFactory
    from nest.core.cli_factory import CLIAppFactory
    from nest.core import Module
    from typing import Any, List

    from src.controllers.zerepy_controller import ZerePyController
    from src.zerepy_service import ZerePyService
    from dotenv import load_dotenv
    import logging
    import os

    load_dotenv()

    log_level = os.getenv("LOG_LEVEL", "INFO")
    if log_level != "INFO":
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d"
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # imports
    IMPORTS = [AgentModule]

    # controllers
    CONTROLLERS = [ZerePyController]

    # providers
    PROVIDERS = [ZerePyService]

    # exports
    EXPORTS: List[Any] = []

    @Module(
        imports=IMPORTS,
        controllers=CONTROLLERS,
        providers=PROVIDERS,
        exports=EXPORTS,
    )
    class ZerePyModule:
        pass

    cli_zerepy = CLIAppFactory().create(ZerePyModule)
    cli_zerepy()
