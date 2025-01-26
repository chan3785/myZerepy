from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseModelConfig(BaseModel, ABC):
    model: str

    def to_json(self) -> dict[str, Any]:
        return self.model_dump()
