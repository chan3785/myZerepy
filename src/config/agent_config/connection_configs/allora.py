import logging
from typing import Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from src.config.agent_config.connection_configs.base_connection import (
    BaseConnectionConfig,
)
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from pydantic_core import ErrorDetails
from pydantic import ValidationError


class AlloraSettings(BaseSettings):
    api_key: ApiKey = Field(validation_alias="ALLORA_API_KEY")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


class AlloraConfig(BaseConnectionConfig):
    chain: BlockchainNetwork
    allora_settings: AlloraSettings
    logger: logging.Logger

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any) -> None:
        # if the connection is not configured, return none
        try:
            data["logger"] = logging.getLogger(f"{self.__class__.__name__}")
            data["allora_settings"] = AlloraSettings()
            super().__init__(**data)

        except Exception as e:
            if isinstance(e, ValidationError):
                errors: list[ErrorDetails] = e.errors()
                for error in errors:
                    print(
                        f'{error.get("msg")}. Invalid Field(s): {".".join(map(str, error.get("loc", [])))}'
                    )
            return

    @property
    def is_llm_provider(self) -> bool:
        return False
