from abc import ABC, abstractmethod
import logging
from typing import Any

from pydantic import ValidationError
from pydantic_core import ErrorDetails
from ...base_config import BaseConfig, BaseSettings

MODEL_ERRORS: dict[str, list[ErrorDetails]] = {}


class BaseModelSettings(BaseSettings, ABC):
    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                MODEL_ERRORS[self.__class__.__name__] = e.errors()
            elif isinstance(e, AttributeError):
                pass
            else:
                print(type(e))


class BaseModelConfig(BaseConfig, ABC):
    model: str

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                MODEL_ERRORS[self.__class__.__name__] = e.errors()
            elif isinstance(e, AttributeError):
                pass
            else:
                print(type(e))

    @abstractmethod
    def _get_client(self) -> Any:
        pass
