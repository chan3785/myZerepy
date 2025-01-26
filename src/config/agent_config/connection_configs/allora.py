from typing import Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from src.config.types import BlockchainNetwork
from src.config.types import ApiKey
from pydantic_core import ErrorDetails
from pydantic import ValidationError


class AlloraSettings(BaseSettings):
    api_key: ApiKey = Field(validation_alias="ALLORA_API_KEY")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


class AlloraConfig(BaseModel):
    chain: BlockchainNetwork
    allora_settings: AlloraSettings

    def __init__(self, **data: Any) -> None:
        # if the connection is not configured, return none
        try:
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
