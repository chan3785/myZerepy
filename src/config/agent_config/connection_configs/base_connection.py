from abc import ABC, abstractmethod
import json
import logging
from typing import Any, Optional
from datetime import datetime
from src.config.agent_config.connection_configs.tasks import Task, TimeBasedMultiplier
from ...base_config import BaseConfig, BaseSettings
from pydantic import PositiveFloat


class BaseConnectionSettings(BaseSettings, ABC):
    pass


class BaseConnectionConfig(BaseConfig, ABC):
    tasks: dict[str, Task] = {}

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        stuff = self.list_class_methods(BaseConnectionConfig)

    def validate_tasks(self, cls: object) -> dict[str, Task]:
        class_methods = self.list_class_methods(cls)
        for k, v in self.tasks.items():
            if k not in class_methods:
                raise Exception(
                    f"Task {k} is not a valid task for this connection. valid connections: {json.dumps(class_methods,indent=4)}"
                )
        return self.tasks
