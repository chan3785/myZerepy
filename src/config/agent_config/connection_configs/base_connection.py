from abc import ABC, abstractmethod
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
    pass
