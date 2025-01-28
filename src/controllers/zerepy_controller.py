import json
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from src.zerepy_service import ZerePyService
import logging

logger = logging.getLogger(__name__)


@CliController("zerepy")
class ZerePyController:
    def __init__(self, zerepy_service: ZerePyService):
        self.zerepy_service = zerepy_service

    @CliCommand("version")
    def version(self) -> None:
        res = self.zerepy_service.version()
        logger.info(res)
