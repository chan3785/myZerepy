from abc import ABC, abstractmethod
from typing import Any, Dict
from src.lib.base_config import BaseConfig, BaseConfigException
from src.utils.deep_dict import deep_get
import logging

logger = logging.getLogger(__name__)

connections: list[str] = []


class BaseConnectionConfig(BaseConfig, ABC):
    cfg: dict[str, Any] = {}

    def __init__(
        self,
        cfg: dict[str, Any],
    ) -> None:
        try:
            self.cfg = deep_get(cfg, [self.connections_key(), self.config_key()])
            self.add_connection(self.config_key())

            super().__init__(self.cfg)

        except Exception as e:
            raise BaseConfigException(f"Error loading {self.config_key()} config: {e}")

    @staticmethod
    @abstractmethod
    def config_key() -> str:
        pass

    @staticmethod
    def connections_key() -> str:
        return "connections"

    @property
    @abstractmethod
    def is_llm_provider(self) -> bool:
        pass

    @staticmethod
    def add_connection(connection: str) -> None:
        connections.append(connection)

    @staticmethod
    def list_connections() -> list[str]:
        return connections
