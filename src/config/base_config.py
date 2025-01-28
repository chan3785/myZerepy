from abc import ABC
import logging
from typing import Any
from pydantic import BaseModel as PydanticBaseModel, ValidationError
from pydantic_core import ErrorDetails
from pydantic_settings import BaseSettings as PydanticBaseSettings


class BaseSettings(PydanticBaseSettings, ABC):
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
            else:
                raise e


class BaseConfig(PydanticBaseModel, ABC):
    logger: logging.Logger

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        stuff = self.list_class_methods()
        try:
            data["logger"] = logging.getLogger(f"{self.__class__.__name__}")
            super().__init__(**data)
        except Exception as e:
            if isinstance(e, ValidationError):
                errors: list[ErrorDetails] = e.errors()
                for error in errors:
                    print(
                        f'{error.get("msg")}. Invalid Field(s): {".".join(map(str, error.get("loc", [])))}'
                    )
            else:
                raise e

    def list_class_methods(self, cls: object | None = None) -> list[str]:
        if cls is None:
            cls = self
        return [
            func
            for func in dir(cls)
            if callable(getattr(cls, func, None)) and not func.startswith("_")
        ]
