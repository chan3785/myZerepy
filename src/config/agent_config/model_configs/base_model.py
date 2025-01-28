from abc import ABC, abstractmethod
import logging
from typing import Any
from ...base_config import BaseConfig, BaseSettings


class BaseModelSettings(BaseSettings, ABC):
    pass


class BaseModelConfig(BaseConfig, ABC):
    model: str

    @abstractmethod
    def _get_client(self) -> Any:
        pass
