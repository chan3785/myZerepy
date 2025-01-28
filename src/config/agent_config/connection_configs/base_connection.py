from abc import ABC, abstractmethod
import json
import logging
from typing import Any, Optional
from datetime import datetime

from pydantic_core import ErrorDetails
from src.config.agent_config.connection_configs.tasks import Task, TimeBasedMultiplier
from ...base_config import BaseConfig, BaseSettings
from pydantic import PositiveFloat, ValidationError


class BaseConnectionSettings(BaseSettings, ABC):
    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                errors: list[ErrorDetails] = e.errors()
                for error in errors:
                    print(
                        f'{error.get("msg")}. Invalid Field(s): {".".join(map(str, error.get("loc", [])))}'
                    )
            elif isinstance(e, AttributeError):
                print(f"WARNING: {e}")
            else:
                print(type(e))


class BaseConnectionConfig(BaseConfig, ABC):
    tasks: dict[str, Task] = {}

    def __init__(self, **data: Any) -> None:
        try:
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                errors: list[ErrorDetails] = e.errors()
                for error in errors:
                    print(
                        f'{error.get("msg")}. Invalid Field(s): {".".join(map(str, error.get("loc", [])))}'
                    )
            elif isinstance(e, AttributeError):
                print(f"WARNING: {e}")
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
