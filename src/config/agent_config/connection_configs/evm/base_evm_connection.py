from abc import ABC, abstractmethod
import json
import logging
from typing import Any, Optional
from datetime import datetime

from pydantic_core import ErrorDetails
from src.config.agent_config.connection_configs.tasks import Task, TimeBasedMultiplier
from pydantic import PositiveFloat, ValidationError

from src.config.base_config import BaseConfig, BaseSettings

EVM_CONNECTION_ERRORS: dict[str, list[ErrorDetails]] = {}


class BaseEvmSettings(BaseSettings, ABC):
    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                EVM_CONNECTION_ERRORS[self.__class__.__name__] = e.errors()
            elif isinstance(e, AttributeError):
                pass
            else:
                print(type(e))


class BaseEvmConfig(BaseConfig, ABC):
    tasks: dict[str, Task] = {}

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                EVM_CONNECTION_ERRORS[self.__class__.__name__] = e.errors()
            elif isinstance(e, AttributeError):
                pass
            else:
                print(type(e))

    def validate_tasks(self, cls: object) -> dict[str, Task]:
        class_methods = self.list_class_methods(cls)
        for k, v in self.tasks.items():
            if k not in class_methods:
                raise Exception(
                    f"Task {k} is not a valid task for this connection. valid connections: {json.dumps(class_methods,indent=4)}"
                )
        return self.tasks

    @abstractmethod
    def _get_client(self) -> Any:
        pass
