from abc import ABC
import logging
from typing import Any
from pydantic import BaseModel as PydanticBaseModel, ValidationError
from pydantic_core import ErrorDetails
from pydantic_settings import BaseSettings as PydanticBaseSettings
from ..lib import deep_pretty_print


class BaseSettings(PydanticBaseSettings, ABC):
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    # def __init__(self, **data: Any) -> None:
    # try:
    #    super().__init__(**data)
    # except Exception as e:
    #    if isinstance(e, ValidationError):
    #        errors: list[ErrorDetails] = e.errors()
    #        for error in errors:
    #            print(
    #                f'{error.get("msg")}. Invalid Field(s): {".".join(map(str, error.get("loc", [])))}'
    #            )
    #    elif isinstance(e, AttributeError):
    #        print(f"Error: {e}")
    #    else:
    #        raise e


class BaseConfig(PydanticBaseModel, ABC):
    logger: logging.Logger = logging.getLogger(__name__)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def list_class_methods(self, cls: object | None = None) -> list[str]:
        if cls is None:
            cls = self
        return [
            func
            for func in dir(cls)
            if callable(getattr(cls, func, None)) and not func.startswith("_")
        ]

    def pretty_print(self) -> str:
        blacklisted_fields = ["logger", "settings"]
        return deep_pretty_print(
            self.model_dump(), blacklisted_fields=blacklisted_fields, partial_match=True
        )
