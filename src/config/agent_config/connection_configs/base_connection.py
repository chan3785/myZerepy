from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseConnectionConfig(BaseModel, ABC):

    @property
    @abstractmethod
    def is_llm_provider(self) -> bool:
        pass

    def to_json(self) -> dict[str, Any]:
        return self.model_dump()
